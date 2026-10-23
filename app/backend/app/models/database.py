import os
import uuid
import json
import logging
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from ..config import settings

logger = logging.getLogger("hr_bot.database")

Base = declarative_base()

# -------------------------------------------------------------
# Models: DBSession & DBAnswer (SQLAlchemy + Mongo Compatible)
# -------------------------------------------------------------
class DBUser(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, default="Candidate")
    is_guest = Column(Integer, default=1)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    sessions = relationship("DBSession", back_populates="user")

class DBSession(Base):
    __tablename__ = "interview_sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    role_id = Column(String, nullable=False)
    role_title = Column(String, nullable=False)
    interview_type = Column(String, default="all")
    language = Column(String, default="en")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    overall_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    content_score = Column(Float, default=0.0)
    status = Column(String, default="in_progress")
    is_demo = Column(Integer, default=0)

    user = relationship("DBUser", back_populates="sessions")
    answers = relationship("DBAnswer", back_populates="session", cascade="all, delete-orphan")

    def __init__(self, **kwargs):
        if "id" not in kwargs or not kwargs["id"]:
            kwargs["id"] = str(uuid.uuid4())
        if "created_at" not in kwargs or kwargs["created_at"] is None:
            kwargs["created_at"] = datetime.now(timezone.utc)
        super().__init__(**kwargs)
        self.id = kwargs["id"]
        self.created_at = kwargs["created_at"]
        self._cached_answers = kwargs.get("answers", None)

    @classmethod
    def from_mongo(cls, doc):
        d = dict(doc)
        d.pop("_id", None)
        if "created_at" in d and isinstance(d["created_at"], str):
            try:
                d["created_at"] = datetime.fromisoformat(d["created_at"])
            except Exception:
                d["created_at"] = datetime.now(timezone.utc)
        obj = cls(**d)
        return obj

    def to_mongo(self):
        fields = [
            "id", "user_id", "role_id", "role_title", "interview_type", "language",
            "created_at", "overall_score", "confidence_score", "clarity_score",
            "content_score", "status", "is_demo"
        ]
        res = {}
        for k in fields:
            val = getattr(self, k, None)
            if isinstance(val, datetime):
                res[k] = val
            elif val is not None:
                res[k] = val
        if "id" not in res:
            res["id"] = self.id
        if "created_at" not in res or res["created_at"] is None:
            res["created_at"] = self.created_at or datetime.now(timezone.utc)
        return res

class DBAnswer(Base):
    __tablename__ = "session_answers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("interview_sessions.id"), nullable=False)
    question_id = Column(String, nullable=False)
    question_text = Column(Text, nullable=False)
    transcript = Column(Text, default="")
    duration_seconds = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    completeness_score = Column(Float, default=0.0)
    structure_score = Column(Float, default=0.0)
    content_score = Column(Float, default=0.0)
    clarity_score = Column(Float, default=0.0)
    confidence_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    feedback = Column(Text, default="")
    improvement_tips = Column(Text, default="[]")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    session = relationship("DBSession", back_populates="answers")

    def __init__(self, **kwargs):
        if "id" not in kwargs or not kwargs["id"]:
            kwargs["id"] = str(uuid.uuid4())
        if "created_at" not in kwargs or kwargs["created_at"] is None:
            kwargs["created_at"] = datetime.now(timezone.utc)
        super().__init__(**kwargs)
        self.id = kwargs["id"]
        self.created_at = kwargs["created_at"]

    @classmethod
    def from_mongo(cls, doc):
        d = dict(doc)
        d.pop("_id", None)
        if "created_at" in d and isinstance(d["created_at"], str):
            try:
                d["created_at"] = datetime.fromisoformat(d["created_at"])
            except Exception:
                d["created_at"] = datetime.now(timezone.utc)
        return cls(**d)

    def to_mongo(self):
        fields = [
            "id", "session_id", "question_id", "question_text", "transcript",
            "duration_seconds", "relevance_score", "completeness_score",
            "structure_score", "content_score", "clarity_score",
            "confidence_score", "overall_score", "feedback", "improvement_tips", "created_at"
        ]
        res = {}
        for k in fields:
            val = getattr(self, k, None)
            if isinstance(val, datetime):
                res[k] = val
            elif val is not None:
                res[k] = val
        if "id" not in res:
            res["id"] = self.id
        if "created_at" not in res or res["created_at"] is None:
            res["created_at"] = self.created_at or datetime.now(timezone.utc)
        return res

# -------------------------------------------------------------
# Determine Backend: MongoDB Atlas vs SQLite Fallback
# -------------------------------------------------------------
db_url = os.getenv("DATABASE_URL") or os.getenv("MONGODB_URI") or settings.DATABASE_URL
is_mongo = bool(db_url and (db_url.startswith("mongodb://") or db_url.startswith("mongodb+srv://")))

_mongo_client = None
_mongo_db = None

if is_mongo:
    try:
        import pymongo
        logger.info("[Database] Connecting to MongoDB Atlas cluster...")
        _mongo_client = pymongo.MongoClient(db_url, serverSelectionTimeoutMS=5000)
        _mongo_db = _mongo_client.get_database("interview_simulator")
        logger.info("[Database] MongoDB Atlas connection established successfully.")
    except Exception as e:
        logger.error(f"[Database] Failed to connect to MongoDB Atlas ({e}). Falling back to SQLite.")
        is_mongo = False

# SQLite Engine (used when not using MongoDB or on local dev fallback)
sqlite_engine = None
SessionLocal = None

if not is_mongo:
    sqlite_url = settings.DATABASE_URL if "sqlite" in settings.DATABASE_URL else "sqlite:///./interview_simulator.db"
    sqlite_engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sqlite_engine)

# -------------------------------------------------------------
# MongoDB Session & Query Emulation Layer
# -------------------------------------------------------------
class MongoQuery:
    def __init__(self, model_class, mongo_db):
        self.model_class = model_class
        self.mongo_db = mongo_db
        self.collection = mongo_db["sessions"] if model_class == DBSession else mongo_db["answers"]
        self.filter_dict = {}
        self.sort_criteria = None
        self._skip = 0
        self._limit = 0

    def filter(self, *clauses):
        for c in clauses:
            if hasattr(c, "left") and hasattr(c, "right"):
                col_name = c.left.name if hasattr(c.left, "name") else str(c.left)
                val = c.right.value if hasattr(c.right, "value") else c.right
                self.filter_dict[col_name] = val
            elif isinstance(c, dict):
                self.filter_dict.update(c)
        return self

    def order_by(self, *criteria):
        self.sort_criteria = [("created_at", -1)]
        return self

    def offset(self, n: int):
        self._skip = n
        return self

    def limit(self, n: int):
        self._limit = n
        return self

    def count(self) -> int:
        return self.collection.count_documents(self.filter_dict)

    def first(self):
        doc = self.collection.find_one(self.filter_dict)
        if not doc:
            return None
        obj = self.model_class.from_mongo(doc)
        if isinstance(obj, DBSession):
            ans_docs = self.mongo_db["answers"].find({"session_id": obj.id}).sort("created_at", 1)
            obj._cached_answers = [DBAnswer.from_mongo(a) for a in ans_docs]
        return obj

    def all(self):
        cursor = self.collection.find(self.filter_dict)
        if self.sort_criteria:
            cursor = cursor.sort(self.sort_criteria)
        if self._skip:
            cursor = cursor.skip(self._skip)
        if self._limit:
            cursor = cursor.limit(self._limit)
        results = []
        for d in cursor:
            obj = self.model_class.from_mongo(d)
            if isinstance(obj, DBSession):
                ans_docs = self.mongo_db["answers"].find({"session_id": obj.id}).sort("created_at", 1)
                obj._cached_answers = [DBAnswer.from_mongo(a) for a in ans_docs]
            results.append(obj)
        return results

class MongoSession:
    def __init__(self, mongo_db):
        self.mongo_db = mongo_db

    def query(self, model_class):
        return MongoQuery(model_class, self.mongo_db)

    def add(self, obj):
        col = self.mongo_db["sessions"] if isinstance(obj, DBSession) else self.mongo_db["answers"]
        doc = obj.to_mongo()
        col.update_one({"id": obj.id}, {"$set": doc}, upsert=True)

    def commit(self):
        pass

    def flush(self):
        pass

    def refresh(self, obj):
        col = self.mongo_db["sessions"] if isinstance(obj, DBSession) else self.mongo_db["answers"]
        doc = col.find_one({"id": obj.id})
        if doc:
            for k, v in doc.items():
                if k != "_id" and hasattr(obj, k):
                    setattr(obj, k, v)
            if isinstance(obj, DBSession):
                ans_docs = self.mongo_db["answers"].find({"session_id": obj.id}).sort("created_at", 1)
                obj._cached_answers = [DBAnswer.from_mongo(a) for a in ans_docs]

    def close(self):
        pass

# -------------------------------------------------------------
# Demo Data Seeder
# -------------------------------------------------------------
def seed_demo_sessions(db):
    """Seeds 4 realistic historical benchmark sessions if no demo sessions exist."""
    demo_count = db.query(DBSession).filter(DBSession.is_demo == 1).count()
    if demo_count > 0:
        return

    sample_sessions = [
        {
            "id": "sess-demo-swe-01",
            "role_id": "software_engineer",
            "role_title": "Software Engineer",
            "created_at": datetime(2026, 8, 20, 14, 22, 0, tzinfo=timezone.utc),
            "overall_score": 74.5,
            "content_score": 72.0,
            "clarity_score": 76.0,
            "confidence_score": 78.0,
            "status": "completed",
            "is_demo": 1,
            "answers": [
                {
                    "question_id": "swe_tech_01",
                    "question_text": "Can you explain the core principles of Object-Oriented Programming (OOP) and give a brief real-world example of Polymorphism?",
                    "transcript": "OOP is built on encapsulation, abstraction, inheritance, and polymorphism. For polymorphism, consider a payment processor where different gateways implement the same execute payment method.",
                    "duration_seconds": 38.5,
                    "relevance_score": 8.0,
                    "completeness_score": 7.0,
                    "structure_score": 7.5,
                    "content_score": 75.0,
                    "clarity_score": 76.0,
                    "confidence_score": 78.0,
                    "overall_score": 75.8,
                    "feedback": "Clear explanation of the 4 pillars. Good payment gateway analogy.",
                    "improvement_tips": ["Mention interface-based polymorphism vs class inheritance."]
                }
            ]
        },
        {
            "id": "sess-demo-pm-02",
            "role_id": "product_manager",
            "role_title": "Product Manager",
            "created_at": datetime(2026, 8, 28, 10, 15, 0, tzinfo=timezone.utc),
            "overall_score": 81.0,
            "content_score": 83.0,
            "clarity_score": 79.0,
            "confidence_score": 81.0,
            "status": "completed",
            "is_demo": 1,
            "answers": [
                {
                    "question_id": "pm_strat_01",
                    "question_text": "How do you prioritize competing engineering and business requests when roadmap capacity is constrained?",
                    "transcript": "I utilize the RICE framework combined with strategic alignment metrics. We quantify reach and impact against effort, while ensuring core platform reliability SLAs are guarded.",
                    "duration_seconds": 44.0,
                    "relevance_score": 8.5,
                    "completeness_score": 8.2,
                    "structure_score": 8.5,
                    "content_score": 84.0,
                    "clarity_score": 79.0,
                    "confidence_score": 81.0,
                    "overall_score": 81.6,
                    "feedback": "Strong structured prioritization framework with good stakeholder awareness.",
                    "improvement_tips": ["Include a specific example of handling executive escalations."]
                }
            ]
        },
        {
            "id": "sess-demo-ds-03",
            "role_id": "data_scientist",
            "role_title": "Data Scientist",
            "created_at": datetime(2026, 9, 5, 16, 40, 0, tzinfo=timezone.utc),
            "overall_score": 84.2,
            "content_score": 86.0,
            "clarity_score": 82.0,
            "confidence_score": 85.0,
            "status": "completed",
            "is_demo": 1,
            "answers": [
                {
                    "question_id": "ds_eval_01",
                    "question_text": "When would you prefer ROC-AUC over Precision-Recall curves in evaluating imbalanced classification systems?",
                    "transcript": "In highly imbalanced regimes like fraud detection where the negative class dominates, ROC-AUC can present an overly optimistic curve because FPR stays low. PR curves directly expose precision trade-offs.",
                    "duration_seconds": 42.0,
                    "relevance_score": 9.0,
                    "completeness_score": 8.5,
                    "structure_score": 8.5,
                    "content_score": 87.0,
                    "clarity_score": 82.0,
                    "confidence_score": 85.0,
                    "overall_score": 84.9,
                    "feedback": "Sharp and accurate breakdown of true positive vs false positive rate distortion in imbalanced datasets.",
                    "improvement_tips": ["Address threshold calibration and cost-matrix integration."]
                }
            ]
        },
        {
            "id": "sess-demo-swe-04",
            "role_id": "software_engineer",
            "role_title": "Software Engineer",
            "created_at": datetime(2026, 9, 12, 11, 5, 0, tzinfo=timezone.utc),
            "overall_score": 89.2,
            "content_score": 91.0,
            "clarity_score": 88.0,
            "confidence_score": 88.0,
            "status": "completed",
            "is_demo": 1,
            "answers": [
                {
                    "question_id": "swe_sys_02",
                    "question_text": "Describe how you would design a globally distributed rate limiting tier with low latency overhead.",
                    "transcript": "We implement a token bucket algorithm at the edge API gateway utilizing local in-memory token buffers backed by Redis clusters using sliding window logs with asynchronous batch sync to minimize cross-region latency.",
                    "duration_seconds": 49.0,
                    "relevance_score": 9.5,
                    "completeness_score": 9.0,
                    "structure_score": 9.2,
                    "content_score": 92.5,
                    "clarity_score": 88.0,
                    "confidence_score": 88.0,
                    "overall_score": 89.8,
                    "feedback": "Exceptional architectural clarity. Clear trade-off analysis between local in-memory accuracy and cross-region consensus latency.",
                    "improvement_tips": ["Discuss fallback behavior if the Redis synchronization cluster degrades."]
                }
            ]
        }
    ]

    for s in sample_sessions:
        ans_data = s.pop("answers")
        session_obj = DBSession(**s)
        db.add(session_obj)
        db.flush()
        for a in ans_data:
            tips = a.pop("improvement_tips", [])
            a["improvement_tips"] = json.dumps(tips)
            ans_obj = DBAnswer(session_id=session_obj.id, **a)
            db.add(ans_obj)
    db.commit()

# -------------------------------------------------------------
# Init & Dependency Providers
# -------------------------------------------------------------
def init_db():
    """Initializes schemas/indexes and optionally seeds benchmark sessions."""
    if is_mongo and _mongo_db is not None:
        try:
            _mongo_db["sessions"].create_index("id", unique=True)
            _mongo_db["sessions"].create_index([("created_at", -1)])
            _mongo_db["answers"].create_index("session_id")
            _mongo_db["answers"].create_index([("session_id", 1), ("question_id", 1)])
            logger.info("[Database] MongoDB Atlas indexes initialized.")
            
            if settings.DEMO_MODE:
                session = MongoSession(_mongo_db)
                seed_demo_sessions(session)
        except Exception as e:
            logger.error(f"[Database] Error initializing MongoDB: {e}")
    elif sqlite_engine is not None:
        Base.metadata.create_all(bind=sqlite_engine)
        if settings.DEMO_MODE and SessionLocal is not None:
            db = SessionLocal()
            try:
                seed_demo_sessions(db)
            finally:
                db.close()

def get_db():
    """FastAPI Dependency: Yields MongoSession or SQLAlchemy Session."""
    if is_mongo and _mongo_db is not None:
        session = MongoSession(_mongo_db)
        try:
            yield session
        finally:
            session.close()
    elif SessionLocal is not None:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        raise RuntimeError("No database engine configured.")
