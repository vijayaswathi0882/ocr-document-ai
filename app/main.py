from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime
from typing import List, Optional
import logging
from app.config import get_settings
from app.database import get_db, init_db, SessionLocal
from app.services.ocr_service import OCRService
from app.services.nlp_service import NLPService
from app.services.storage_service import StorageService
from app.services.document_processor import DocumentProcessor
from app.models.document import Document
from app.schemas.document import DocumentResponse, DocumentCreate, ProcessingStatus
from app.api.document_analysis import router as analysis_router

from fastapi import FastAPI
from app.routes.document_routes import router as document_router

app = FastAPI()
app.include_router(document_router)
app.include_router(analysis_router, prefix="/api/v1", tags=["Document Analysis"])



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Real Estate Document Processor",
    description="AI-powered document processing for real estate documents",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

settings = get_settings()

# Initialize services
ocr_service = OCRService()
nlp_service = NLPService()
storage_service = StorageService()
document_processor = DocumentProcessor(ocr_service, nlp_service, storage_service)

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    init_db()
    logger.info("Real Estate Document Processor started successfully")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Real Estate Document Processor API",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db_session=Depends(get_db)
):
    """Upload and process a real estate document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, JPG, JPEG, PNG, or TIFF files."
            )
        
        # Save file temporarily
        upload_path = f"./uploads/{file.filename}"
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Create document record
        document_data = DocumentCreate(
            filename=file.filename,
            file_path=upload_path,
            status="uploaded"
        )
        
        document = Document(**document_data.dict())
        db_session.add(document)
        db_session.commit()
        db_session.refresh(document)
        
        # Process document in background
        background_tasks.add_task(
            process_document_background,
            document.id,
            upload_path
        )
        
        logger.info(f"Document {file.filename} uploaded successfully with ID: {document.id}")
        
        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            status=document.status,
            upload_timestamp=document.upload_timestamp,
            message="Document uploaded successfully. Processing started."
        )
        
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")

async def process_document_background(document_id: int, file_path: str):
    """Background task to process document"""
    try:
        db_session = SessionLocal()
        try:
            document = db_session.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document with ID {document_id} not found")
                return
            
            # Update status to processing
            document.status = "processing"
            db_session.commit()
            
            # Process the document
            result = await document_processor.process_document(file_path)
            
            # Update document with results
            # Store only structured data, not raw text
            document.extracted_data = result.get("extracted_data", {})
            document.confidence_score = result.get("confidence_score", 0.0)
            document.status = "completed"
            document.processed_timestamp = datetime.now()
            
            db_session.commit()
            
            logger.info(f"Document {document_id} processed successfully")
        finally:
            db_session.close()
            
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        # Update status to failed
        db_session = SessionLocal()
        try:
            document = db_session.query(Document).filter(Document.id == document_id).first()
            if document:
                document.status = "failed"
                document.error_message = str(e)
                db_session.commit()
        finally:
            db_session.close()

@app.get("/documents/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int, db_session=Depends(get_db)):
    """Get document details and processing status"""
    document = db_session.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=document.id,
        filename=document.filename,
        status=document.status,
        upload_timestamp=document.upload_timestamp,
        processed_timestamp=document.processed_timestamp,
        extracted_data=document.extracted_data,
        confidence_score=document.confidence_score,
        error_message=document.error_message
    )

@app.get("/documents", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db_session=Depends(get_db)
):
    """List all documents with optional filtering"""
    query = db_session.query(Document)
    
    if status:
        query = query.filter(Document.status == status)
    
    documents = query.offset(skip).limit(limit).all()
    
    return [
        DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            status=doc.status,
            upload_timestamp=doc.upload_timestamp,
            processed_timestamp=doc.processed_timestamp,
            extracted_data=doc.extracted_data,
            confidence_score=doc.confidence_score
        )
        for doc in documents
    ]

@app.get("/documents/{document_id}/search")
async def search_document(
    document_id: int,
    query: str,
    db_session=Depends(get_db)
):
    """Search within a specific document's extracted data"""
    document = db_session.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Search in extracted structured data only
    extracted_data = document.extracted_data or {}
    
    matches = []
    
    # Search in extracted data
    for key, value in extracted_data.items():
        if isinstance(value, str) and query.lower() in value.lower():
            matches.append({"type": "extracted_field", "field": key, "value": value})
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str) and query.lower() in item.lower():
                    matches.append({"type": "extracted_field", "field": key, "value": item})
    
    return {"query": query, "matches": matches}

@app.get("/analytics/summary")
async def get_analytics_summary(db_session=Depends(get_db)):
    """Get analytics summary of processed documents"""
    total_documents = db_session.query(Document).count()
    completed_documents = db_session.query(Document).filter(Document.status == "completed").count()
    processing_documents = db_session.query(Document).filter(Document.status == "processing").count()
    failed_documents = db_session.query(Document).filter(Document.status == "failed").count()
    
    return {
        "total_documents": total_documents,
        "completed_documents": completed_documents,
        "processing_documents": processing_documents,
        "failed_documents": failed_documents,
        "success_rate": (completed_documents / total_documents * 100) if total_documents > 0 else 0
    }