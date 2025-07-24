import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main document processing orchestrator"""
    
    def __init__(self, ocr_service, nlp_service, storage_service):
        self.ocr_service = ocr_service
        self.nlp_service = nlp_service
        self.storage_service = storage_service
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document through the full pipeline"""
        try:
            logger.info(f"Starting document processing for: {file_path}")
            
            # Step 1: Extract text using OCR
            logger.info("Step 1: Extracting text with OCR")
            ocr_result = await self.ocr_service.extract_text_from_file(file_path)
            
            if "error" in ocr_result:
                raise Exception(f"OCR failed: {ocr_result['error']}")
            
            raw_text = ocr_result.get("raw_text", "")
            if not raw_text:
                raise Exception("No text extracted from document")
            
            logger.info(f"OCR completed. Extracted {len(raw_text)} characters")
            
            # Step 2: Process with NLP
            logger.info("Step 2: Processing with NLP")
            structured_data = await self.nlp_service.extract_structured_data(raw_text)
            
            if "error" in structured_data:
                logger.warning(f"NLP processing had issues: {structured_data['error']}")
                structured_data = {"error": structured_data["error"]}
            
            logger.info("NLP processing completed")
            
            # Step 3: Calculate overall confidence
            confidence_score = self._calculate_confidence(ocr_result, structured_data)
            
            # Step 4: Upload to storage (optional, for backup)
            try:
                blob_name = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file_path.split('/')[-1]}"
                storage_result = await self.storage_service.upload_file(file_path, blob_name)
                logger.info(f"File uploaded to storage: {storage_result}")
            except Exception as e:
                logger.warning(f"Storage upload failed: {e}")
            
            # Compile final result
            result = {
                "extracted_data": structured_data,
                "confidence_score": confidence_score,
                "ocr_metadata": {
                    "pages": ocr_result.get("pages", 0),
                    "word_count": ocr_result.get("word_count", 0),
                    "ocr_confidence": ocr_result.get("confidence", 0.0)
                },
                "processing_timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            logger.info("Document processing completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                "extracted_data": {},
                "confidence_score": 0.0,
                "error": str(e),
                "processing_timestamp": datetime.now().isoformat(),
                "status": "failed"
            }
    
    def _calculate_confidence(self, ocr_result: Dict[str, Any], structured_data: Dict[str, Any]) -> float:
        """Calculate overall confidence score"""
        try:
            ocr_confidence = ocr_result.get("confidence", 0.0)
            
            # Get confidence from structured data analysis
            analysis_confidence = structured_data.get("confidence_score", 0.0)
            
            # Count non-null extracted fields for additional validation
            field_count = 0
            total_fields = 20  # Total extractable fields
            
            if isinstance(structured_data, dict) and "error" not in structured_data:
                for key, value in structured_data.items():
                    if key == "confidence_score":
                        continue
                    if value is not None and value != "" and value != []:
                        field_count += 1
            
            extraction_confidence = field_count / total_fields
            
            # Weighted average: OCR confidence, analysis confidence, and field extraction
            overall_confidence = (ocr_confidence * 0.3) + (analysis_confidence * 0.5) + (extraction_confidence * 0.2)
            
            return round(overall_confidence, 2)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.0