---
name: database-mastery
description: >-
  Use this skill when designing schemas, setting up database connections, writing CRUD operations, configuring vector databases (Pinecone, pgvector), connecting MongoDB Atlas, Supabase, or Firebase Firestore during hackathons.
---

# Database Mastery for Hackathons

A rock-solid database setup accounts for up to **35% of technical scoring**. Never settle for dummy mockups when real data persistence, auth, and vector search take under 5 minutes to wire up.

---

## 1. Quick Decision Matrix

| Requirement | Top Recommendation | Free Tier Limits | Setup Time |
|---|---|---|---|
| **Fastest NoSQL / Flexible JSON** | **MongoDB Atlas** | 512 MB forever free (M0 cluster) | 3 mins |
| **Relational SQL + Instant Auth + Realtime** | **Supabase** (Postgres) | 500 MB database, 50,000 MAU | 4 mins |
| **Realtime Multi-User Sync (Chat / Collab)** | **Firebase Firestore** | 1 GB storage, 50k reads/day | 4 mins |
| **AI Embeddings & Semantic Search** | **Pinecone** / **Supabase pgvector** | 1 index, 100k vectors free | 3 mins |

---

## 2. Production-Ready Code Snippets

### A. MongoDB Atlas (Mongoose + Next.js App Router)
Install: `npm install mongoose`

```typescript
// lib/db.ts
import mongoose from 'mongoose';

const MONGODB_URI = process.env.MONGODB_URI!;

if (!MONGODB_URI) {
  throw new Error('Please define the MONGODB_URI environment variable');
}

let cached = (global as any).mongoose || { conn: null, promise: null };

export async function connectDB() {
  if (cached.conn) return cached.conn;
  if (!cached.promise) {
    cached.promise = mongoose.connect(MONGODB_URI, {
      bufferCommands: false,
    }).then((m) => m);
  }
  cached.conn = await cached.promise;
  return cached.conn;
}
```

```typescript
// models/Project.ts
import mongoose, { Schema, model, models } from 'mongoose';

const ProjectSchema = new Schema({
  title: { type: String, required: true },
  description: String,
  aiInsights: [String],
  createdAt: { type: Date, default: Date.now },
});

export const Project = models.Project || model('Project', ProjectSchema);
```

---

### B. Supabase (PostgreSQL + Real-time + Vector)
Install: `npm install @supabase/supabase-js`

```typescript
// lib/supabase.ts
import { createClient } from '@supabase/supabase-js';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

// Realtime Listener Hook Pattern
export function subscribeToTable(table: string, onInsert: (payload: any) => void) {
  return supabase
    .channel(`${table}_changes`)
    .on('postgres_changes', { event: 'INSERT', schema: 'public', table }, onInsert)
    .subscribe();
}
```

#### Vector Search in Supabase (pgvector)
Run once in Supabase SQL Editor:
```sql
create extension if not exists vector;

create table documents (
  id bigserial primary key,
  content text,
  embedding vector(768) -- matches Gemini embeddings
);

create or replace function match_documents (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (id bigint, content text, similarity float)
language sql stable as $$
  select id, content, 1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  where 1 - (documents.embedding <=> query_embedding) > match_threshold
  order by similarity desc
  limit match_count;
$$;
```

---

### C. Pinecone (Serverless Vector DB for RAG)
Install: `npm install @pinecone-database/pinecone`

```typescript
// lib/pinecone.ts
import { Pinecone } from '@pinecone-database/pinecone';

const pc = new Pinecone({ apiKey: process.env.PINECONE_API_KEY! });
const index = pc.index(process.env.PINECONE_INDEX_NAME || 'hackathon-index');

export async function querySimilar(vector: number[], topK = 5) {
  const result = await index.query({
    vector,
    topK,
    includeMetadata: true,
  });
  return result.matches;
}
```

---

### D. Firebase Firestore (Realtime Sync)
Install: `npm install firebase`

```typescript
// lib/firebase.ts
import { initializeApp, getApps, getApp } from 'firebase/app';
import { getFirestore, collection, addDoc, onSnapshot, query, orderBy } from 'firebase/firestore';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
};

const app = getApps().length ? getApp() : initializeApp(firebaseConfig);
export const db = getFirestore(app);
```

---

## 3. Hackathon Security & Environment Protocol
1. **Never commit `.env` files**: All DB URIs, passwords, and service role keys must live in `.env.local`.
2. **Whitelist All IPs in Atlas**: In MongoDB Atlas -> Network Access -> Add IP Address -> Select **"Allow Access from Anywhere" (`0.0.0.0/0`)**. Hackathon venue IPs change and Vercel serverless functions have dynamic IPs. If you forget this, your deployed app will fail to connect.
3. **Use Anonymous / Public Keys for Frontend**: Never put Supabase `service_role` key in frontend code; use `anon_key` with Row Level Security (RLS) or call via Next.js `/api` route.
