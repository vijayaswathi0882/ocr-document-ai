# Real Estate Document Processor - Pure Backend API

A pure backend API system for processing real estate documents using OCR and NLP with Azure services and MySQL database.

## 🏗️ Backend Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Upload   │───▶│   OCR Service   │───▶│   NLP Service   │
│   (FastAPI)     │    │  (Azure Form    │    │ (Azure Text     │
│                 │    │   Recognizer)   │    │  Analytics)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Azure Blob    │    │   Document      │    │   MySQL         │
│   Storage       │    │   Processor     │    │   Database      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start - Backend Only

### Prerequisites
- Python 3.8+
- MySQL Server 8.0+

### Step 1: Install MySQL
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install mysql-server
sudo systemctl start mysql

# macOS
brew install mysql && brew services start mysql

# Windows - Download from MySQL website
```

### Step 2: Setup Backend
```bash
# Setup MySQL database and environment
python setup_mysql.py

# Start the backend API server
python run_local.py
```

### Step 3: Test Backend API
```bash
# Test all API endpoints
python test_api.py
```

## 📁 Backend File Structure

```
real-estate-document-processor/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration
│   ├── database.py             # MySQL setup
│   ├── models/
│   │   └── document.py         # Database models
│   ├── schemas/
│   │   └── document.py         # API schemas
│   └── services/
│       ├── ocr_service.py      # OCR processing
│       ├── nlp_service.py      # NLP processing
│       ├── storage_service.py  # File storage
│       └── document_processor.py
├── uploads/                    # File upload directory
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables
├── run_local.py               # Development server
├── test_api.py                # API testing
├── setup_mysql.py             # MySQL setup
└── docker-compose.yml         # Docker with MySQL
```

## 📤 How to Upload Files to Backend

### Method 1: Using Python requests
```python
import requests

# Upload a document
url = "http://localhost:8000/documents/upload"
files = {'file': open('your_document.pdf', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### Method 2: Using curl command
```bash
# Upload PDF document
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_document.pdf"

# Upload image document
curl -X POST "http://localhost:8000/documents/upload" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@lease_agreement.jpg"
```

### Method 3: Using API Documentation Interface
1. Start server: `python run_local.py`
2. Open browser: `http://localhost:8000/docs`
3. Find `/documents/upload` endpoint
4. Click "Try it out"
5. Choose file and click "Execute"

## 🔍 How to Check Uploaded Files

### Check Upload Status
```bash
# Get document by ID
curl -X GET "http://localhost:8000/documents/1"

# List all documents
curl -X GET "http://localhost:8000/documents"

# Search within document
curl -X GET "http://localhost:8000/documents/1/search?query=rent"
```

### Check MySQL Database
```bash
# Connect to MySQL
mysql -u root -p

# Use database
USE real_estate_docs;

# View uploaded documents
SELECT id, filename, status, upload_timestamp FROM documents;

# View extracted data
SELECT id, filename, extracted_data FROM documents WHERE status = 'completed';
```

### Check File System
```bash
# Check uploaded files directory
ls -la uploads/

# Check logs
ls -la logs/
```

## 📊 Backend API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| POST | `/documents/upload` | Upload document |
| GET | `/documents/{id}` | Get document details |
| GET | `/documents` | List all documents |
| GET | `/documents/{id}/search` | Search in document |
| GET | `/analytics/summary` | Processing stats |

## 🗄️ MySQL Database Schema

```sql
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    status VARCHAR(50) DEFAULT 'uploaded',
    upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_timestamp DATETIME NULL,
    raw_text LONGTEXT NULL,
    extracted_data JSON NULL,
    confidence_score FLOAT DEFAULT 0.0,
    error_message TEXT NULL
);
```

## 🧪 Testing Your Backend

### 1. Start Backend Server
```bash
python run_local.py
# Server runs on http://localhost:8000
```

### 2. Upload Test Document
```bash
# Create sample document
echo "LEASE AGREEMENT
Property: 123 Main St
Landlord: John Smith
Tenant: Jane Doe
Rent: $1200/month" > sample_lease.txt

# Upload via curl
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@sample_lease.txt"
```

### 3. Check Processing Results
```bash
# Check document status
curl -X GET "http://localhost:8000/documents/1"

# View all documents
curl -X GET "http://localhost:8000/documents"
```

## 🐳 Docker Backend Setup

```bash
# Start MySQL + Backend with Docker
docker-compose up -d

# Check logs
docker-compose logs -f app

# Stop services
docker-compose down
```

## 🔧 Environment Configuration

Create `.env` file:
```env
# MySQL Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/real_estate_docs
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=real_estate_docs

# File Storage
LOCAL_UPLOAD_PATH=./uploads

# Azure Services (Optional)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_COGNITIVE_SERVICES_ENDPOINT=
AZURE_COGNITIVE_SERVICES_KEY=
AZURE_TEXT_ANALYTICS_ENDPOINT=
AZURE_TEXT_ANALYTICS_KEY=
```

This is a pure backend API system with no frontend components. You can integrate it with any frontend framework or use it directly via API calls.