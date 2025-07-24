const express = require('express');
const multer = require('multer');
const sqlite3 = require('sqlite3').verbose();
const axios = require('axios');
const FormData = require('form-data');
const cors = require('cors');
const fs = require('fs').promises;
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: async (req, file, cb) => {
    const uploadDir = './uploads';
    try {
      await fs.mkdir(uploadDir, { recursive: true });
    } catch (error) {
      console.error('Error creating upload directory:', error);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({ 
  storage: storage,
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    const allowedTypes = /pdf|jpg|jpeg|png/;
    const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = allowedTypes.test(file.mimetype);
    
    if (mimetype && extname) {
      return cb(null, true);
    } else {
      cb(new Error('Only PDF, JPG, JPEG, and PNG files are allowed'));
    }
  }
});

// SQLite Database setup
const db = new sqlite3.Database('./database.db', (err) => {
  if (err) {
    console.error('❌ SQLite connection failed:', err.message);
  } else {
    console.log('✅ Connected to SQLite database');
  }
});

// Promisify database methods
const dbAsync = {
  run: (sql, params = []) => {
    return new Promise((resolve, reject) => {
      db.run(sql, params, function(err) {
        if (err) reject(err);
        else resolve({ lastID: this.lastID, changes: this.changes });
      });
    });
  },
  get: (sql, params = []) => {
    return new Promise((resolve, reject) => {
      db.get(sql, params, (err, row) => {
        if (err) reject(err);
        else resolve(row);
      });
    });
  },
  all: (sql, params = []) => {
    return new Promise((resolve, reject) => {
      db.all(sql, params, (err, rows) => {
        if (err) reject(err);
        else resolve(rows);
      });
    });
  }
};

// Initialize database tables
async function initDatabase() {
  try {
    console.log('🔄 Initializing SQLite database...');
    
    // Create documents table
    await dbAsync.run(`
      CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_path TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        mime_type TEXT NOT NULL,
        status TEXT DEFAULT 'uploaded' CHECK(status IN ('uploaded', 'processing', 'completed', 'failed')),
        extracted_text TEXT,
        entities TEXT,
        key_value_pairs TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
      )
    `);
    
    console.log('✅ Database tables initialized');
  } catch (error) {
    console.error('❌ Database initialization failed:', error.message);
  }
}

// Azure Form Recognizer OCR
async function extractTextWithOCR(filePath) {
  try {
    const fileBuffer = await fs.readFile(filePath);
    const formData = new FormData();
    formData.append('file', fileBuffer, path.basename(filePath));
    
    const response = await axios.post(
      `${process.env.AZURE_COGNITIVE_SERVICES_ENDPOINT}/formrecognizer/documentModels/prebuilt-read:analyze?api-version=2023-07-31`,
      formData,
      {
        headers: {
          'Ocp-Apim-Subscription-Key': process.env.AZURE_COGNITIVE_SERVICES_KEY,
          ...formData.getHeaders()
        }
      }
    );
    
    // Get operation location for polling
    const operationLocation = response.headers['operation-location'];
    
    // Poll for results
    let result;
    let attempts = 0;
    const maxAttempts = 30;
    
    while (attempts < maxAttempts) {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
      
      const resultResponse = await axios.get(operationLocation, {
        headers: {
          'Ocp-Apim-Subscription-Key': process.env.AZURE_COGNITIVE_SERVICES_KEY
        }
      });
      
      if (resultResponse.data.status === 'succeeded') {
        result = resultResponse.data;
        break;
      } else if (resultResponse.data.status === 'failed') {
        throw new Error('OCR processing failed');
      }
      
      attempts++;
    }
    
    if (!result) {
      throw new Error('OCR processing timed out');
    }
    
    // Extract text from pages
    let extractedText = '';
    if (result.analyzeResult && result.analyzeResult.pages) {
      for (const page of result.analyzeResult.pages) {
        if (page.lines) {
          for (const line of page.lines) {
            extractedText += line.content + '\n';
          }
        }
      }
    }
    
    return extractedText.trim();
  } catch (error) {
    console.error('OCR extraction failed:', error.message);
    throw error;
  }
}

// Azure Text Analytics NLP
async function extractEntities(text) {
  try {
    const response = await axios.post(
      `${process.env.AZURE_TEXT_ANALYTICS_ENDPOINT}/text/analytics/v3.1/entities/recognition/general`,
      {
        documents: [
          {
            id: "1",
            language: "en",
            text: text.substring(0, 5120) // Limit text length
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
    
    const entities = response.data.documents[0]?.entities || [];
    return entities.map(entity => ({
      text: entity.text,
      category: entity.category,
      confidence: entity.confidenceScore
    }));
  } catch (error) {
    console.error('Entity extraction failed:', error.message);
    return [];
  }
}

// Routes
app.get('/', (req, res) => {
  res.json({
    message: 'Real Estate Document Processor API',
    version: '1.0.0',
    database: 'SQLite',
    endpoints: {
      upload: 'POST /documents/upload',
      status: 'GET /documents/:id',
      list: 'GET /documents'
    }
  });
});

app.get('/health', async (req, res) => {
  try {
    // Test SQLite database connection
    await dbAsync.get('SELECT 1 as test');
    
    res.json({
      status: 'healthy',
      database: 'SQLite connected',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Health check failed:', error.message);
    res.status(500).json({
      status: 'unhealthy',
      database: 'SQLite disconnected',
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

app.post('/documents/upload', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }
    
    // Insert document record
    const result = await dbAsync.run(
      `INSERT INTO documents (filename, original_filename, file_path, file_size, mime_type, status) 
       VALUES (?, ?, ?, ?, ?, 'uploaded')`,
      [req.file.filename, req.file.originalname, req.file.path, req.file.size, req.file.mimetype]
    );
    
    const documentId = result.lastID;
    
    console.log(`✅ Document ${req.file.originalname} uploaded successfully with ID: ${documentId}`);
    
    // Process document in background
    processDocumentBackground(documentId, req.file.path);
    
    res.json({
      message: 'Document uploaded successfully',
      document_id: documentId,
      filename: req.file.originalname,
      status: 'uploaded'
    });
    
  } catch (error) {
    console.error('Upload error:', error);
    res.status(500).json({ error: 'Upload failed: ' + error.message });
  }
});

app.get('/documents/:id', async (req, res) => {
  try {
    const documentId = req.params.id;
    
    const document = await dbAsync.get(
      'SELECT * FROM documents WHERE id = ?',
      [documentId]
    );
    
    if (!document) {
      return res.status(404).json({ error: 'Document not found' });
    }
    
    // Parse JSON fields
    if (document.entities) {
      try {
        document.entities = JSON.parse(document.entities);
      } catch (e) {
        document.entities = [];
      }
    }
    if (document.key_value_pairs) {
      try {
        document.key_value_pairs = JSON.parse(document.key_value_pairs);
      } catch (e) {
        document.key_value_pairs = {};
      }
    }
    
    res.json(document);
    
  } catch (error) {
    console.error('Get document error:', error);
    res.status(500).json({ error: 'Failed to retrieve document: ' + error.message });
  }
});

app.get('/documents', async (req, res) => {
  try {
    const rows = await dbAsync.all(
      'SELECT id, filename, original_filename, file_size, mime_type, status, created_at, updated_at FROM documents ORDER BY created_at DESC'
    );
    
    res.json({
      documents: rows,
      total: rows.length
    });
    
  } catch (error) {
    console.error('List documents error:', error);
    res.status(500).json({ error: 'Failed to retrieve documents: ' + error.message });
  }
});

// Background processing function
async function processDocumentBackground(documentId, filePath) {
  try {
    console.log(`🔄 Starting background processing for document ${documentId}`);
    
    // Update status to processing
    await dbAsync.run(
      'UPDATE documents SET status = ? WHERE id = ?',
      ['processing', documentId]
    );
    
    // Extract text using OCR
    console.log(`📄 Extracting text from document ${documentId}`);
    const extractedText = await extractTextWithOCR(filePath);
    
    // Extract entities using NLP
    console.log(`🧠 Extracting entities from document ${documentId}`);
    const entities = await extractEntities(extractedText);
    
    // Update document with results
    await dbAsync.run(
      'UPDATE documents SET status = ?, extracted_text = ?, entities = ? WHERE id = ?',
      ['completed', extractedText, JSON.stringify(entities), documentId]
    );
    
    console.log(`✅ Document ${documentId} processed successfully`);
    
  } catch (error) {
    console.error(`❌ Error processing document ${documentId}:`, error.message);
    
    try {
      await dbAsync.run(
        'UPDATE documents SET status = ? WHERE id = ?',
        ['failed', documentId]
      );
    } catch (dbError) {
      console.error('Failed to update document status:', dbError.message);
    }
  }
}

// Start server
async function startServer() {
  try {
    await initDatabase();
    
    app.listen(PORT, '0.0.0.0', () => {
      console.log('\n' + '='.repeat(60));
      console.log('🚀 Real Estate Document Processor - Node.js Server');
      console.log('='.repeat(60));
      console.log(`📡 Server running on http://localhost:${PORT}`);
      console.log(`📚 API Health: http://localhost:${PORT}/health`);
      console.log(`📋 Upload endpoint: POST http://localhost:${PORT}/documents/upload`);
      console.log(`💾 Database: SQLite (./database.db)`);
      console.log('='.repeat(60));
    });
    
  } catch (error) {
    console.error('❌ Failed to start server:', error.message);
    process.exit(1);
  }
}

startServer();