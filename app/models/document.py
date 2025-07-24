from sqlalchemy import Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.sql import func
from app.database import Base

class Document(Base):
    """Document model for storing processed real estate documents"""
    
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    status = Column(String(50), default="uploaded")  # uploaded, processing, completed, failed
    
    # Timestamps
    upload_timestamp = Column(DateTime, default=func.now())
    processed_timestamp = Column(DateTime, nullable=True)
    
    # OCR Results
    raw_text = Column(Text, nullable=True)
    
    # Extracted Data (JSON)
    extracted_data = Column(JSON, nullable=True)
    
    # Confidence and Error Handling
    confidence_score = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', status='{self.status}')>"