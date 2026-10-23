import { MongoClient } from 'mongodb';

const uri = process.env.MONGODB_URI;

if (!uri) {
  console.warn('⚠️ Warning: MONGODB_URI is not defined in environment variables.');
}

let client: MongoClient;
let clientPromise: Promise<MongoClient>;

declare global {
  var _mongoClientPromise: Promise<MongoClient> | undefined;
}

if (!uri) {
  clientPromise = Promise.reject(new Error('Please add MONGODB_URI to .env.local'));
} else if (process.env.NODE_ENV === 'development') {
  // In development mode, use a global variable so the MongoClient is not repeated
  // on hot reloads.
  if (!global._mongoClientPromise) {
    client = new MongoClient(uri);
    global._mongoClientPromise = client.connect();
  }
  clientPromise = global._mongoClientPromise;
} else {
  // In production (Vercel), create a standard client
  client = new MongoClient(uri);
  clientPromise = client.connect();
}

export default clientPromise;

export async function getDatabase(dbName = 'hackathon') {
  const client = await clientPromise;
  return client.db(dbName);
}
