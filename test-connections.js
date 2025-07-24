const mysql = require('mysql2/promise');
const axios = require('axios');
const fs = require('fs').promises;
require('dotenv').config();

async function testConnections() {
  console.log('\n' + '='.repeat(60));
  console.log('🧪 Testing Azure and MySQL Connections');
  console.log('='.repeat(60));
  
  let allTestsPassed = true;
  
  // Test MySQL Database
  console.log('\n📊 Testing MySQL Database Connection...');
  try {
    console.log(`   Connecting to: ${process.env.MYSQL_HOST}:${process.env.MYSQL_PORT}`);
    console.log(`   Database: ${process.env.MYSQL_DATABASE}`);
    console.log(`   User: ${process.env.MYSQL_USER}`);
    
    const connection = await Promise.race([
      mysql.createConnection({
        host: process.env.MYSQL_HOST,
        port: process.env.MYSQL_PORT,
        user: process.env.MYSQL_USER,
        password: process.env.MYSQL_PASSWORD,
        database: process.env.MYSQL_DATABASE,
        connectTimeout: 30000,
        acquireTimeout: 30000,
        timeout: 30000
      }),
      new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Connection timeout after 30 seconds')), 30000)
      )
    ]);
    
    const connection_old = await mysql.createConnection({
      host: process.env.MYSQL_HOST,
      port: process.env.MYSQL_PORT,
      user: process.env.MYSQL_USER,
      password: process.env.MYSQL_PASSWORD,
      database: process.env.MYSQL_DATABASE,
      connectTimeout: 30000,
      acquireTimeout: 30000,
      timeout: 30000
    });
    
    await connection.ping();
    console.log('✅ MySQL connection successful');
    
    // Test table creation
    await connection.execute(`
      CREATE TABLE IF NOT EXISTS test_table (
        id INT AUTO_INCREMENT PRIMARY KEY,
        test_data VARCHAR(255)
      )
    `);
    console.log('✅ MySQL table operations working');
    
    await connection.execute('DROP TABLE IF EXISTS test_table');
    await connection.end();
    
  } catch (error) {
    console.log('❌ MySQL connection failed:', error.message);
    allTestsPassed = false;
  }
  
  // Test Azure Form Recognizer
  console.log('\n🔍 Testing Azure Form Recognizer...');
  try {
    const response = await axios.get(
      `${process.env.AZURE_COGNITIVE_SERVICES_ENDPOINT}/formrecognizer/info?api-version=2023-07-31`,
      {
        headers: {
          'Ocp-Apim-Subscription-Key': process.env.AZURE_COGNITIVE_SERVICES_KEY
        }
      }
    );
    console.log('✅ Azure Form Recognizer connection successful');
  } catch (error) {
    console.log('❌ Azure Form Recognizer failed:', error.response?.data || error.message);
    allTestsPassed = false;
  }
  
  // Test Azure Text Analytics
  console.log('\n🧠 Testing Azure Text Analytics...');
  try {
    const response = await axios.post(
      `${process.env.AZURE_TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/entities/recognition/general`,
      {
        documents: [
          {
            id: "1",
            language: "en",
            text: "This is a test document for entity recognition."
          }
        ]
      },
      {
        headers: {
          'Ocp-Apim-Subscription-Key': process.env.AZURE_TEXT_ANALYTICS_KEY,
          'Content-Type': 'application/json'
        }
      }
    );
    console.log('✅ Azure Text Analytics connection successful');
  } catch (error) {
    console.log('❌ Azure Text Analytics failed:', error.response?.data || error.message);
    allTestsPassed = false;
  }
  
  // Test Azure Blob Storage
  console.log('\n☁️ Testing Azure Blob Storage...');
  try {
    // Simple connection test by parsing connection string
    const connectionString = process.env.AZURE_STORAGE_CONNECTION_STRING;
    if (connectionString && connectionString.includes('AccountName') && connectionString.includes('AccountKey')) {
      console.log('✅ Azure Blob Storage connection string is valid');
    } else {
      throw new Error('Invalid connection string format');
    }
  } catch (error) {
    console.log('❌ Azure Blob Storage configuration failed:', error.message);
    allTestsPassed = false;
  }
  
  // Summary
  console.log('\n' + '='.repeat(60));
  if (allTestsPassed) {
    console.log('🎉 All connection tests passed! Ready to start the server.');
    console.log('Run: npm start');
  } else {
    console.log('⚠️ Some tests failed. Please check your configuration.');
  }
  console.log('='.repeat(60));
}

testConnections().catch(console.error);