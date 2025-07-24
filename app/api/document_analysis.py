"""
Standalone API endpoint for document analysis
Returns structured JSON data without storing in database
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import tempfile
import os
from app.services.document_analyzer import DocumentAnalyzer
from app.services.ocr_service import OCRService

router = APIRouter()

@router.post("/analyze")
async def analyze_document_endpoint(file: UploadFile = File(...)):
    """
    Analyze uploaded document and return structured JSON data
    
    This endpoint:
    1. Accepts file upload (PDF, JPG, PNG, TIFF)
    2. Extracts text using OCR
    3. Analyzes text and extracts structured data
    4. Returns clean JSON format (no raw text)
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png', '.tiff')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF, JPG, JPEG, PNG, or TIFF files."
            )
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Extract text using OCR
            ocr_service = OCRService()
            ocr_result = await ocr_service.extract_text_from_file(temp_file_path)
            
            if "error" in ocr_result:
                raise HTTPException(status_code=500, detail=f"OCR failed: {ocr_result['error']}")
            
            raw_text = ocr_result.get("raw_text", "")
            if not raw_text:
                raise HTTPException(status_code=500, detail="No text extracted from document")
            
            # Analyze document and extract structured data
            analyzer = DocumentAnalyzer()
            structured_data = analyzer.analyze_document(raw_text)
            
            # Return only structured data in JSON format
            return JSONResponse(content=structured_data)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@router.post("/analyze-text")
async def analyze_text_endpoint(text_data: dict):
    """
    Analyze raw text and return structured JSON data
    
    Request body: {"text": "document text content"}
    """
    try:
        text = text_data.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text provided")
        
        # Analyze text and extract structured data
        analyzer = DocumentAnalyzer()
        structured_data = analyzer.analyze_document(text)
        
        # Return only structured data in JSON format
        return JSONResponse(content=structured_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text analysis failed: {str(e)}")