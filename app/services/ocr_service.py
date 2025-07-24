import asyncio
import logging
from typing import Dict, Any, Optional
from PIL import Image
import PyPDF2
import io
import os

try:
    from azure.ai.formrecognizer import DocumentAnalysisClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from app.config import get_settings

logger = logging.getLogger(__name__)

class OCRService:
    """Service for Optical Character Recognition using Azure Form Recognizer"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = None
        
        if AZURE_AVAILABLE and self.settings.azure_cognitive_services_endpoint:
            try:
                self.client = DocumentAnalysisClient(
                    endpoint=self.settings.azure_cognitive_services_endpoint,
                    credential=AzureKeyCredential(self.settings.azure_cognitive_services_key)
                )
                logger.info("Azure Form Recognizer client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Azure client: {e}")
                self.client = None
        
        if not self.client:
            logger.info("Using local OCR simulation")
    
    async def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """Extract text from a file using OCR"""
        try:
            if self.client:
                return await self._extract_with_azure(file_path)
            else:
                return await self._extract_with_local_simulation(file_path)
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            return {
                "raw_text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _extract_with_azure(self, file_path: str) -> Dict[str, Any]:
        """Extract text using Azure Form Recognizer"""
        try:
            with open(file_path, "rb") as file:
                poller = self.client.begin_analyze_document(
                    "prebuilt-document", 
                    file
                )
                result = poller.result()
            
            # Extract text content
            raw_text = ""
            for page in result.pages:
                for line in page.lines:
                    raw_text += line.content + "\n"
            
            # Calculate average confidence
            confidences = []
            for page in result.pages:
                for word in page.words:
                    if word.confidence:
                        confidences.append(word.confidence)
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "raw_text": raw_text,
                "confidence": avg_confidence,
                "pages": len(result.pages),
                "word_count": len(raw_text.split()) if raw_text else 0
            }
            
        except Exception as e:
            logger.error(f"Azure OCR error: {e}")
            raise
    
    async def _extract_with_local_simulation(self, file_path: str) -> Dict[str, Any]:
        """Local simulation of OCR for development/testing"""
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return await self._extract_from_pdf(file_path)
            elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff']:
                return await self._simulate_image_ocr(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            logger.error(f"Local OCR simulation error: {e}")
            raise
    
    async def _extract_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """Extract text from PDF files"""
        try:
            raw_text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    raw_text += page.extract_text() + "\n"
            
            return {
                "raw_text": raw_text,
                "confidence": 0.95,  # Simulated confidence
                "pages": len(pdf_reader.pages),
                "word_count": len(raw_text.split()) if raw_text else 0
            }
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise
    
    async def _simulate_image_ocr(self, file_path: str) -> Dict[str, Any]:
        """Simulate OCR for image files (for development)"""
        try:
            # In a real implementation, this would use actual OCR
            # For now, return simulated real estate document text
            simulated_text = """
            REAL ESTATE LEASE AGREEMENT
            
            Property Address: 123 Main Street, Anytown, ST 12345
            
            Landlord: John Smith
            Address: 456 Oak Avenue, Anytown, ST 12345
            Phone: (555) 123-4567
            
            Tenant: Jane Doe
            Address: 789 Pine Road, Anytown, ST 12345
            Phone: (555) 987-6543
            
            Lease Terms:
            Monthly Rent: $1,200.00
            Security Deposit: $1,200.00
            Lease Start Date: January 1, 2024
            Lease End Date: December 31, 2024
            
            Property Details:
            Type: Residential Apartment
            Bedrooms: 2
            Bathrooms: 1
            Square Footage: 850 sq ft
            
            Additional Terms:
            - Pets allowed with additional deposit
            - Utilities included: Water, Sewer
            - Parking: 1 assigned space
            
            Signatures:
            Landlord: _________________ Date: ___________
            Tenant: __________________ Date: ___________
            """
            
            return {
                "raw_text": simulated_text.strip(),
                "confidence": 0.92,  # Simulated confidence
                "pages": 1,
                "word_count": len(simulated_text.split())
            }
            
        except Exception as e:
            logger.error(f"Image OCR simulation error: {e}")
            raise