require('dotenv').config({ path: '.env.local' });
const mongoose = require('mongoose');

async function testConnection() {
  const uri = process.env.MONGODB_URI;
  if (!uri || uri.includes('<password>') || uri.includes('YOUR_PASSWORD')) {
    console.log('⚠️ Please set your valid MONGODB_URI in .env.local first!');
    process.exit(1);
  }

  console.log('🔄 Attempting connection to MongoDB Atlas...');
  try {
    const start = Date.now();
    await mongoose.connect(uri);
    const latency = Date.now() - start;
    console.log(`✅ MongoDB Atlas Connection SUCCESS! (Latency: ${latency}ms)`);

    // Quick test collection ping
    const testDoc = await mongoose.connection.db.collection('healthcheck').insertOne({
      status: 'active',
      testedAt: new Date(),
      hackathon: 'DITE Hackathon 2026-27'
    });
    console.log('✅ Write Test Passed! Inserted ID:', testDoc.insertedId);

    await mongoose.disconnect();
    console.log('🎉 Database is 100% ready for the hackathon!');
    process.exit(0);
  } catch (error) {
    console.error('❌ MongoDB Connection Error:', error.message);
    if (error.message.includes('bad auth') || error.message.includes('Authentication failed')) {
      console.log('👉 Hint: Check your database username and password in the connection string.');
    } else if (error.message.includes('whitelist') || error.message.includes('timed out') || error.message.includes('MongoServerSelectionError')) {
      console.log('👉 Hint: Make sure you added 0.0.0.0/0 (Allow access from anywhere) in Atlas Network Access!');
    }
    process.exit(1);
  }
}

testConnection();
