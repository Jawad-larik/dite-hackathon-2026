# 📚 Hackathon Starter: Master Cheatsheets & Recommended Libraries

Curated from [sahat/hackathon-starter](https://github.com/sahat/hackathon-starter) (35k+ ⭐) and modernized for 2026 AI hackathons.

---

## 1. Recommended Node.js Libraries

| Package | Install Command | Best For | Code Recipe |
|---|---|---|---|
| **`filesize`** | `npm i filesize` | Human-readable byte formatting | `import { filesize } from 'filesize'; filesize(265318); // "265.32 kB"` |
| **`numeral`** | `npm i numeral` | Numbers, currencies, percentages | `import numeral from 'numeral'; numeral(12500).format('$0,0.00'); // "$12,500.00"` |
| **`geoip-lite`** | `npm i geoip-lite` | Instant IP to City/Country (No API needed) | `import geoip from 'geoip-lite'; const geo = geoip.lookup(ip);` |
| **`sharp`** | `npm i sharp` | High-speed image compression & WebP | `await sharp(inputBuffer).resize(800).webp().toBuffer();` |
| **`canvas-confetti`** | `npm i canvas-confetti` | Win/Submit celebration explosion | `import confetti from 'canvas-confetti'; confetti();` |
| **`nprogress`** | `npm i nprogress` | Top YouTube-style loading bar | `import NProgress from 'nprogress'; NProgress.start(); NProgress.done();` |

---

## 2. Recommended Client-side Libraries (UI & UX)

- **`sonner`**: Modern toast notifications (`toast.success('Generated in 240ms!')`).
- **`nprogress`**: Slim YouTube-style top progress bar during long AI calls or navigation.
- **`canvas-confetti`**: Explodes celebratory confetti on judge form submission or winning task completion.
- **`lucide-react`**: 1,000+ ultra-clean SVG icons with zero overhead.

---

## 3. Mongoose & MongoDB Cheatsheet

### Connection with Connection Caching
```typescript
import mongoose from 'mongoose';

let cached = (global as any).mongoose || { conn: null, promise: null };

export async function connectDB() {
  if (cached.conn) return cached.conn;
  if (!cached.promise) {
    cached.promise = mongoose.connect(process.env.MONGODB_URI!, { bufferCommands: false });
  }
  cached.conn = await cached.promise;
  return cached.conn;
}
```

### Essential CRUD Operations
```typescript
// 1. Create
const doc = await Project.create({ title: 'AI Assistant', tags: ['hackathon', 'ai'] });

// 2. Read with Sorting & Pagination
const recent = await Project.find()
  .sort({ createdAt: -1 })
  .limit(10)
  .lean();

// 3. Find One & Update (Atomic)
const updated = await Project.findOneAndUpdate(
  { _id: projectId },
  { $set: { status: 'completed' }, $push: { logs: 'Generated output' } },
  { new: true }
);

// 4. Aggregation (Calculate Stats across collection)
const stats = await Project.aggregate([
  { $group: { _id: '$category', totalProjects: { $sum: 1 }, avgScore: { $avg: '$score' } } },
  { $sort: { totalProjects: -1 } }
]);
```

---

## 4. ES6+ & Modern JavaScript Cheatsheet

### Safe Destructuring with Defaults
```javascript
const { model = 'cohere/north-mini-code:free', temperature = 0.7, maxTokens = 1000 } = req.body || {};
```

### Parallel Promise Execution (`Promise.allSettled`)
```javascript
// Run parallel calls without letting one failure break everything
const [aiResult, dbResult] = await Promise.allSettled([
  fetchAICompletion(prompt),
  saveUserAction(userId, prompt)
]);
```

### Clean Async Error Handling
```javascript
export async function safeAsync(promise) {
  try {
    const data = await promise;
    return [data, null];
  } catch (error) {
    return [null, error];
  }
}
// Usage: const [data, err] = await safeAsync(fetchData());
```

---

## 5. JavaScript Date & Relative Time Cheatsheet

```javascript
// Current Unix Timestamp (seconds)
const nowSeconds = Math.floor(Date.now() / 1000);

// Add Time Offsets
const in30Minutes = new Date(Date.now() + 30 * 60 * 1000);
const in24Hours = new Date(Date.now() + 24 * 60 * 60 * 1000);

// Human Readable Relative Time (Intl.RelativeTimeFormat - Built into JS!)
function formatRelativeTime(date) {
  const diffSeconds = Math.round((date.getTime() - Date.now()) / 1000);
  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });
  if (Math.abs(diffSeconds) < 60) return rtf.format(diffSeconds, 'second');
  if (Math.abs(diffSeconds) < 3600) return rtf.format(Math.round(diffSeconds / 60), 'minute');
  if (Math.abs(diffSeconds) < 86400) return rtf.format(Math.round(diffSeconds / 3600), 'hour');
  return rtf.format(Math.round(diffSeconds / 86400), 'day');
}
```
