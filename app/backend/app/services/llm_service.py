import os
import json
import re
import requests
import logging
from typing import Dict, Any, List
from ..config import settings

logger = logging.getLogger("hr_bot.llm")

def extract_json_object(text: str) -> Dict[str, Any]:
    """Extracts JSON object from LLM output, handling markdown fences and reasoning blocks."""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    
    code_block = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', cleaned, re.DOTALL)
    if code_block:
        return json.loads(code_block.group(1))

    first_brace = cleaned.find('{')
    last_brace = cleaned.rfind('}')
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        json_str = cleaned[first_brace:last_brace + 1]
        return json.loads(json_str)

    raise ValueError("No valid JSON structure found in output")

def evaluate_with_local_heuristic(
    question_text: str,
    expected_points: List[str],
    transcript: str,
    role_title: str
) -> Dict[str, Any]:
    """
    Intelligent, deterministic rule-based evaluation engine.
    Guarantees the live interview demo never crashes even under zero connectivity.
    Scores relevance, completeness (rubric keyword hit-ratio), and STAR structural markers.
    """
    # A) Guard clause for insufficient input (< 5 words)
    words = transcript.strip().split()
    if len(words) < 5:
        return {
            'relevance_score': 0.0,
            'completeness_score': 0.0,
            'structure_score': 0.0,
            'content_score': 0.0,
            'feedback': 'No substantive answer detected. Please record a full response.',
            'strengths': [],
            'improvement_tips': ['Provide a complete answer to the question.'],
            'model_used': 'insufficient_input'
        }

    words_clean = re.findall(r'\b[a-zA-Z0-9_\-\']+\b', transcript.lower())
    transcript_text = " ".join(words_clean)
    word_count = len(words_clean)
    
    # 1. Keyword & Expected Points Semantic Matching
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "and", "or", "in", "on", "at", 
        "to", "for", "with", "by", "about", "like", "through", "over", "before", 
        "between", "after", "since", "without", "under", "within", "along", "following", 
        "across", "behind", "beyond", "plus", "except", "but", "up", "out", "around", 
        "down", "off", "above", "near", "it", "this", "that", "these", "those", "can", 
        "could", "should", "would", "may", "might", "must", "shall", "will", "of"
    }
    
    total_rubric_points = len(expected_points)
    matched_points = []
    missed_points = []
    
    for pt in expected_points:
        pt_words = [w for w in re.findall(r'\b[a-zA-Z0-9_\-\']+\b', pt.lower()) if w not in stopwords and len(w) > 3]
        if not pt_words:
            matched_points.append(pt)
            continue
        # Stemming-tolerant matching (e.g. bundle/bundles, method/methods)
        match_count = 0
        for w in pt_words:
            stem = w[:4] if len(w) >= 4 else w
            if any(stem in tw for tw in words_clean):
                match_count += 1
        match_ratio = match_count / max(1, len(pt_words))
        if match_ratio >= 0.30:
            matched_points.append(pt)
        else:
            missed_points.append(pt)
            
    hit_ratio = len(matched_points) / max(1, total_rubric_points)
    # B) Remove artificial floors: max(0.0, ...)
    comp = min(10.0, max(0.0, hit_ratio * 10.0))
    
    # 2. Relevance Scoring
    q_words = [w for w in re.findall(r'\b[a-zA-Z0-9_\-\']+\b', question_text.lower()) if w not in stopwords and len(w) > 3]
    q_overlap = 0
    if q_words:
        for qw in q_words:
            stem = qw[:4] if len(qw) >= 4 else qw
            if any(stem in tw for tw in words_clean):
                q_overlap += 1
        q_overlap_ratio = q_overlap / len(q_words)
    else:
        q_overlap_ratio = 0.5
    
    # If both question overlap and rubric match are zero, it is completely off-topic
    if hit_ratio == 0 and q_overlap_ratio == 0:
        rel = 0.0
    else:
        relevance_signal = max(q_overlap_ratio, hit_ratio * 0.85)
        if q_overlap_ratio > 0 and hit_ratio > 0:
            relevance_signal = min(1.0, relevance_signal + 0.1)
        length_factor = 0.7 if word_count < 10 else 1.0
        rel = min(10.0, max(0.0, relevance_signal * length_factor * 10.0))
    
    # 3. Structural Progression (STAR / Architectural Grammar)
    premise_markers = ["because", "in our system", "the core concept", "first", "architecture", "designed to", "specifically", "fundamentally"]
    mechanism_markers = ["we implemented", "i configured", "by using", "consumers", "leverage", "utilize", "method", "class", "override", "algorithm"]
    outcome_markers = ["resulting in", "this prevented", "reduced latency", "sla", "compromise", "therefore", "trade-off", "performance", "finally"]
    
    has_premise = any(m in transcript_text for m in premise_markers)
    has_mechanism = any(m in transcript_text for m in mechanism_markers)
    has_outcome = any(m in transcript_text for m in outcome_markers)
    
    classes_hit = sum([has_premise, has_mechanism, has_outcome])
    if hit_ratio == 0 and rel == 0:
        struct = 0.0
    elif classes_hit == 3:
        struct = 9.0
    elif classes_hit == 2:
        struct = 7.5
    elif classes_hit == 1:
        struct = 5.0
    else:
        struct = 2.0
        
    content_100 = round((rel * 0.4 + comp * 0.4 + struct * 0.2) * 10.0, 1)
    
    if hit_ratio >= 0.7:
        summary = f"Strong command of foundational concepts for {role_title}. Demonstrates clear technical precision."
    elif hit_ratio >= 0.4:
        summary = f"Solid initial premise with good direction, though some key architectural trade-offs could be further detailed."
    else:
        summary = f"Candidate provided general context, but lacked depth against core rubric requirements."
        
    tips = []
    if missed_points:
        for mp in missed_points[:2]:
            clean_p = re.sub(r'^(mention|explain|provide|discuss|describe)\s+', '', mp, flags=re.IGNORECASE)
            tips.append(f"Explicitly detail: {clean_p}.")
    if not has_outcome:
        tips.append("Conclude responses with tangible results, latency trade-offs, or production metrics.")
    if len(tips) == 0:
        tips.append("Reinforce edge cases and failure recovery semantics in production scenarios.")
        
    return {
        "relevance_score": round(rel, 1),
        "completeness_score": round(comp, 1),
        "structure_score": round(struct, 1),
        "content_score": content_100,
        "feedback": summary,
        "improvement_tips": tips[:2],
        "model_used": "local_heuristic_scorer"
    }

def evaluate_answer_with_llm(
    question_text: str,
    expected_points: List[str],
    transcript: str,
    role_title: str,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Evaluates candidate transcript against question rubric using OpenRouter API (openrouter/free).
    Falls back gracefully to the Local Heuristic Engine on error or timeout.
    """
    if not transcript or len(transcript.strip().split()) < 5:
        is_urdu = language == "ur" or bool(re.search(r'[\u0600-\u06FF]', transcript))
        return {
            "relevance_score": 0.0,
            "completeness_score": 0.0,
            "structure_score": 0.0,
            "content_score": 0.0,
            "feedback": "جواب بہت مختصر یا ناکافی تھا جس کی بنا پر مکمل جانچ نہیں کی جا سکی۔" if is_urdu else "No substantive answer detected. Please record a full response.",
            "improvement_tips": [
                "Provide a complete answer to the question."
            ],
            "model_used": "insufficient_input"
        }

    points_bulleted = "\n".join([f"- {p}" for p in expected_points])
    
    prompt = f"""You are an elite, fair HR and Technical Interviewer assessing a candidate for a {role_title} position.

Interview Question:
\"{question_text}\"

Expected Key Points (Rubric):
{points_bulleted}

Candidate's Spoken Response (Transcribed):
\"{transcript}\"

Evaluate objectively and output ONLY a JSON object with this EXACT structure (no markdown fences, no text outside the JSON):
{{
  "relevance_score": <float 0.0 to 10.0: how directly the candidate answered the prompt>,
  "completeness_score": <float 0.0 to 10.0: coverage of key technical/behavioral concepts>,
  "structure_score": <float 0.0 to 10.0: logical organization, premise, development, outcome>,
  "feedback": "<2-3 sentence constructive evaluation of the candidate's answer depth and delivery>",
  "improvement_tips": [
    "<actionable, specific suggestion 1>",
    "<actionable, specific suggestion 2>"
  ]
}}"""

    # -------------------------------------------------------------
    # STAGE 1: PRIMARY LLM -> Groq qwen/qwen3.8-27b (Ultra-fast <600ms)
    # -------------------------------------------------------------
    groq_api_key = os.getenv("GROQ_API_KEY", "") or getattr(settings, "GROQ_API_KEY", "")
    if groq_api_key:
        try:
            import groq
            groq_model = os.getenv("GROQ_MODEL", "") or getattr(settings, "GROQ_MODEL", "qwen/qwen3.8-27b")
            client = groq.Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                model=groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional technical hiring evaluator who evaluates interview answers strictly following JSON schemas."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_content = completion.choices[0].message.content.strip()
            parsed = extract_json_object(raw_content)
            rel = float(parsed.get("relevance_score", 7.0))
            comp = float(parsed.get("completeness_score", 7.0))
            struct = float(parsed.get("structure_score", 7.0))
            content_100 = round((rel * 0.4 + comp * 0.4 + struct * 0.2) * 10.0, 1)

            logger.info(f"Evaluated via Groq ({groq_model})")
            print(f"[LLM Engine] Evaluated via Groq ({groq_model})")

            return {
                "relevance_score": rel,
                "completeness_score": comp,
                "structure_score": struct,
                "content_score": content_100,
                "feedback": parsed.get("feedback", "Good effort addressing the core concepts."),
                "improvement_tips": parsed.get("improvement_tips", ["Elaborate on specific examples to strengthen your response."]),
                "model_used": f"groq:{groq_model}"
            }
        except Exception as groq_err:
            logger.warning(f"Groq evaluation failed: {groq_err}. Falling back to OpenRouter.")
            print(f"[LLM Engine] Groq primary error ({groq_err}), switching to OpenRouter fallback")

    # -------------------------------------------------------------
    # STAGE 2: FALLBACK LLM -> OpenRouter (cohere/north-mini-code:free)
    # -------------------------------------------------------------
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "") or getattr(settings, "OPENROUTER_API_KEY", "")
    if openrouter_key:
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "AI-Based Interview Simulator"
        }

        payload = {
            "model": getattr(settings, "OPENROUTER_MODEL", "cohere/north-mini-code:free"),
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional technical hiring evaluator who evaluates interview answers strictly following JSON schemas."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=12
            )
            
            if response.status_code == 200:
                res_json = response.json()
                actual_model = res_json.get('model', 'openrouter_model')
                logger.info(f"Evaluated via OpenRouter: {actual_model}")
                print(f"[LLM Engine] Evaluated via OpenRouter: {actual_model}")
                
                raw_content = res_json['choices'][0]['message']['content'].strip()
                parsed = extract_json_object(raw_content)
                rel = float(parsed.get("relevance_score", 7.0))
                comp = float(parsed.get("completeness_score", 7.0))
                struct = float(parsed.get("structure_score", 7.0))
                
                content_100 = round((rel * 0.4 + comp * 0.4 + struct * 0.2) * 10.0, 1)
                
                return {
                    "relevance_score": rel,
                    "completeness_score": comp,
                    "structure_score": struct,
                    "content_score": content_100,
                    "feedback": parsed.get("feedback", "Good effort addressing the core concepts."),
                    "improvement_tips": parsed.get("improvement_tips", ["Elaborate on specific examples to strengthen your response."]),
                    "model_used": f"openrouter:{actual_model}"
                }
            else:
                logger.warning(f"OpenRouter returned {response.status_code}: {response.text}")
                print(f"[LLM Engine] OpenRouter returned {response.status_code}, falling back to Local Heuristic Scorer")
        except Exception as err:
            logger.warning(f"OpenRouter call failed: {err}. Executing local heuristic engine.")
            print(f"[LLM Engine] OpenRouter error ({err}), falling back to Local Heuristic Scorer")

    # -------------------------------------------------------------
    # STAGE 3: LAST RESORT -> Local Deterministic Heuristic Engine
    # -------------------------------------------------------------
    print("[LLM Engine] Using Local Heuristic Scorer (offline resilience guarantee)")
    return evaluate_with_local_heuristic(
        question_text=question_text,
        expected_points=expected_points,
        transcript=transcript,
        role_title=role_title
    )


def _synthesize_heuristic_jd_questions(
    jd: str,
    resume: str = "",
    role: str = "Software Engineer",
    n: int = 5
) -> List[Dict[str, Any]]:
    """
    Synthesizes structured interview questions by extracting key skills/technologies from the JD.
    Guarantees deterministic question generation when all LLMs are unreachable.
    """
    tech_keywords = [
        "Kubernetes", "Docker", "Kafka", "PostgreSQL", "Redis", "Distributed Systems",
        "Microservices", "REST", "GraphQL", "Python", "React", "TypeScript", "AWS",
        "GCP", "CI/CD", "Security", "Scalability", "Concurrency", "Database", "Observability"
    ]
    found_tech = [tech for tech in tech_keywords if re.search(r'\b' + re.escape(tech) + r'\b', jd, re.IGNORECASE)]
    if not found_tech:
        found_tech = ["Core Architecture", "High Availability", "Performance Optimization", "Data Modeling", "Failure Recovery"]

    questions = []
    templates = [
        (
            "How do you architect and tune a production system utilizing {tech} to ensure fault-tolerance and minimal p99 latency?",
            ["High availability clustering", "Failover strategies", "Backpressure and metrics monitoring"],
            "A resilient {tech} topology uses distributed replicas, proactive health probes, and circuit breakers to isolate cascading failures."
        ),
        (
            "Based on the requirements for {role}, how would you implement data consistency and rollback mechanics with {tech}?",
            ["Idempotent operations", "Transactional consistency / outbox pattern", "Automated rollback or dead-letter queue"],
            "We employ unique idempotency identifiers, transactional logging, and automated compensation actions to preserve state consistency."
        ),
        (
            "Describe a production incident or bottleneck you diagnosed involving {tech}, and the systemic steps taken to resolve it.",
            ["Root cause analysis with telemetry", "Immediate triage mitigation", "Long-term architectural guardrails"],
            "I conducted heap and thread dump triage, identified thread contention, refactored connection pooling, and deployed automated alerting."
        ),
        (
            "How do you evaluate architectural trade-offs between delivery velocity and operational scalability when adopting {tech}?",
            ["Quantifiable business requirements", "Operational complexity cost", "Phased migration roadmap"],
            "I weigh latency SLAs and failure domains against development overhead, using modular abstractions to ease future transitions."
        ),
        (
            "In this role, how would you design an automated observability and testing harness for services built on {tech}?",
            ["Distributed tracing (OpenTelemetry)", "Synthetic canary transactions", "Automated integration pipelines"],
            "An end-to-end telemetry harness captures trace spans, tracks error budgets, and runs automated load canaries prior to full rollout."
        )
    ]

    for i in range(min(n, len(templates))):
        tech = found_tech[i % len(found_tech)]
        q_tpl, pts, model_ans = templates[i]
        questions.append({
            "id": f"jd_q_{i+1}",
            "role": role.lower().replace(" ", "_"),
            "type": "technical" if i < 3 else "behavioral",
            "difficulty": "hard" if i % 2 == 0 else "medium",
            "question": q_tpl.format(tech=tech, role=role),
            "expected_points": pts,
            "model_answer": model_ans.format(tech=tech, role=role),
            "time_limit_sec": 90
        })

    return questions


def generate_questions_from_jd(
    jd: str,
    resume: str = "",
    role: str = "Software Engineer",
    n: int = 5
) -> List[Dict[str, Any]]:
    """
    Generates n rubric-tagged interview questions tailored directly to the Job Description and Resume.
    Groq is primary (<800ms), OpenRouter is fallback, followed by a smart heuristic extractor.
    """
    if not jd or not jd.strip():
        return []

    prompt = f"""You are an elite Technical Hiring Bar Raiser designing an interview for a {role} position.

Target Job Description:
\"\"\"{jd.strip()}\"\"\"

Candidate Resume / Profile Highlights:
\"\"\"{resume.strip() if resume and resume.strip() else "None provided - evaluate standard role requirements."}\"\"\"

Generate exactly {n} high-signal, distinct interview questions calibrated directly to the technical requirements, core tools, architectural patterns, and scenarios in this Job Description.

Output ONLY a JSON object with this EXACT structure (no markdown fences, no text outside the JSON):
{{
  "questions": [
    {{
      "id": "jd_q_1",
      "role": "{role.lower().replace(' ', '_')}",
      "type": "technical",
      "difficulty": "medium",
      "question": "<Precise question directly referencing technologies or scenarios from the JD>",
      "expected_points": [
        "<Key technical concept 1>",
        "<Key technical concept 2>",
        "<Key technical concept 3>"
      ],
      "model_answer": "<Authoritative benchmark answer in 2-3 sentences>",
      "time_limit_sec": 90
    }}
  ]
}}"""

    # 1. Primary: Groq Cloud
    groq_api_key = os.getenv("GROQ_API_KEY", "") or getattr(settings, "GROQ_API_KEY", "")
    if groq_api_key:
        try:
            import groq
            groq_model = os.getenv("GROQ_MODEL", "") or getattr(settings, "GROQ_MODEL", "qwen/qwen3.8-27b")
            client = groq.Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                model=groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior technical interviewer who outputs strictly valid JSON schemas."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            raw_content = completion.choices[0].message.content.strip()
            parsed = extract_json_object(raw_content)
            qs = parsed.get("questions", [])
            if isinstance(qs, list) and len(qs) > 0:
                for i, q in enumerate(qs):
                    if "id" not in q:
                        q["id"] = f"jd_q_{i+1}"
                    if "role" not in q:
                        q["role"] = role.lower().replace(" ", "_")
                    if "type" not in q:
                        q["type"] = "technical"
                    if "difficulty" not in q:
                        q["difficulty"] = "medium"
                    if "time_limit_sec" not in q:
                        q["time_limit_sec"] = 90
                logger.info(f"Generated {len(qs)} questions from JD via Groq ({groq_model})")
                print(f"[LLM Engine] Generated {len(qs)} questions from JD via Groq ({groq_model})")
                return qs[:n]
        except Exception as groq_err:
            logger.warning(f"Groq question generation failed: {groq_err}. Trying OpenRouter fallback.")
            print(f"[LLM Engine] Groq question gen error ({groq_err}), trying OpenRouter fallback")

    # 2. Fallback: OpenRouter
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "") or getattr(settings, "OPENROUTER_API_KEY", "")
    if openrouter_key:
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "AI-Based Interview Simulator"
        }
        payload = {
            "model": getattr(settings, "OPENROUTER_MODEL", "cohere/north-mini-code:free"),
            "messages": [
                {
                    "role": "system",
                    "content": "You are a senior technical interviewer who outputs strictly valid JSON schemas."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=12
            )
            if response.status_code == 200:
                raw_content = response.json()['choices'][0]['message']['content'].strip()
                parsed = extract_json_object(raw_content)
                qs = parsed.get("questions", [])
                if isinstance(qs, list) and len(qs) > 0:
                    for i, q in enumerate(qs):
                        if "id" not in q:
                            q["id"] = f"jd_q_{i+1}"
                        if "role" not in q:
                            q["role"] = role.lower().replace(" ", "_")
                        if "type" not in q:
                            q["type"] = "technical"
                        if "difficulty" not in q:
                            q["difficulty"] = "medium"
                        if "time_limit_sec" not in q:
                            q["time_limit_sec"] = 90
                    logger.info(f"Generated {len(qs)} questions from JD via OpenRouter")
                    print(f"[LLM Engine] Generated {len(qs)} questions from JD via OpenRouter")
                    return qs[:n]
        except Exception as err:
            logger.warning(f"OpenRouter question generation error: {err}")
            print(f"[LLM Engine] OpenRouter question gen error ({err})")

    # 3. Last Resort: Rule-Based Heuristic Question Synthesizer from JD
    print("[LLM Engine] Using Heuristic Question Synthesizer for JD")
    return _synthesize_heuristic_jd_questions(jd, resume, role, n)


def generate_adaptive_follow_up(
    question_text: str,
    answer_text: str,
    jd_text: str = "",
    role: str = "Software Engineer"
) -> Optional[str]:
    """
    Generates ONE adaptive follow-up question based on the candidate's last answer and the JD.
    If the answer has fewer than 5 words, skips generation and returns None.
    """
    words = answer_text.strip().split()
    if len(words) < 5:
        return None

    prompt = f"""You are an elite Technical Hiring Interviewer assessing a candidate for a {role} position.

Target Job Description:
\"\"\"{jd_text.strip() if jd_text and jd_text.strip() else "Standard technical requirements for " + role}\"\"\"

Question Asked:
\"{question_text}\"

Candidate's Answer:
\"{answer_text}\"

Based on the candidate's specific answer and the JD requirements, generate exactly ONE concise, probing follow-up question (1-2 sentences) that challenges a technical trade-off, clarifies an architectural detail, or tests edge-case handling.

Output ONLY a JSON object with this EXACT structure (no markdown fences, no text outside the JSON):
{{
  "follow_up_question": "<One concise, sharp follow-up question>"
}}"""

    # 1. Primary: Groq Cloud
    groq_api_key = os.getenv("GROQ_API_KEY", "") or getattr(settings, "GROQ_API_KEY", "")
    if groq_api_key:
        try:
            import groq
            groq_model = os.getenv("GROQ_MODEL", "") or getattr(settings, "GROQ_MODEL", "qwen/qwen3.8-27b")
            client = groq.Groq(api_key=groq_api_key)
            completion = client.chat.completions.create(
                model=groq_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional technical interviewer who outputs strictly valid JSON schemas."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=250,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            raw_content = completion.choices[0].message.content.strip()
            parsed = extract_json_object(raw_content)
            q = parsed.get("follow_up_question", "").strip()
            if q:
                logger.info(f"Generated adaptive follow-up via Groq ({groq_model})")
                print(f"[LLM Engine] Generated adaptive follow-up via Groq ({groq_model})")
                return q
        except Exception as groq_err:
            logger.warning(f"Groq follow-up generation failed: {groq_err}. Trying OpenRouter fallback.")
            print(f"[LLM Engine] Groq follow-up error ({groq_err}), trying OpenRouter fallback")

    # 2. Fallback: OpenRouter
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "") or getattr(settings, "OPENROUTER_API_KEY", "")
    if openrouter_key:
        headers = {
            "Authorization": f"Bearer {openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://localhost",
            "X-Title": "AI-Based Interview Simulator"
        }
        payload = {
            "model": getattr(settings, "OPENROUTER_MODEL", "cohere/north-mini-code:free"),
            "messages": [
                {
                    "role": "system",
                    "content": "You are a professional technical interviewer who outputs strictly valid JSON schemas."
                },
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                raw_content = response.json()['choices'][0]['message']['content'].strip()
                parsed = extract_json_object(raw_content)
                q = parsed.get("follow_up_question", "").strip()
                if q:
                    logger.info("Generated adaptive follow-up via OpenRouter")
                    print("[LLM Engine] Generated adaptive follow-up via OpenRouter")
                    return q
        except Exception as err:
            logger.warning(f"OpenRouter follow-up generation error: {err}")
            print(f"[LLM Engine] OpenRouter follow-up error ({err})")

    # 3. Last Resort: Heuristic Follow-up
    return "Could you elaborate on the failure recovery and monitoring strategy for that approach under unexpected production load?"


