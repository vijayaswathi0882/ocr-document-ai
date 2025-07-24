from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class DocumentCreate(BaseModel):
    """Schema for creating a new document"""
    filename: str
    file_path: str
    status: str = "uploaded"

class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: int
    filename: str
    status: str
    upload_timestamp: datetime
    processed_timestamp: Optional[datetime] = None
    raw_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    confidence_score: Optional[float] = None
    error_message: Optional[str] = None
    message: Optional[str] = None
    
    class Config:
        from_attributes = True

class ProcessingStatus(BaseModel):
    """Schema for processing status"""
    document_id: int
    status: str
    progress: float
    message: str