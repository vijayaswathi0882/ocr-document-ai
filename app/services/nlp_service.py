import re
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from app.config import get_settings

logger = logging.getLogger(__name__)

class NLPService:
    """Service for Natural Language Processing using Azure Text Analytics"""

    def __init__(self):
        self.settings = get_settings()
        self.client = None

        if AZURE_AVAILABLE and self.settings.azure_text_analytics_endpoint:
            try:
                self.client = TextAnalyticsClient(
                    endpoint=self.settings.azure_text_analytics_endpoint,
                    credential=AzureKeyCredential(self.settings.azure_text_analytics_key)
                )
                logger.info("Azure Text Analytics client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Azure Text Analytics client: {e}")
                self.client = None

        if not self.client:
            logger.info("Using local NLP simulation")

    async def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract named entities from text"""
        try:
            if self.client:
                return await self._extract_entities_azure(text)
            else:
                return await self._extract_entities_local(text)
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return {"entities": [], "error": str(e)}

    async def _extract_entities_azure(self, text: str) -> Dict[str, Any]:
        """Extract entities using Azure Text Analytics"""
        try:
            documents = [text]
            result = self.client.recognize_entities(documents=documents)[0]

            entities = []
            for entity in result.entities:
                entities.append({
                    "text": entity.text,
                    "category": entity.category,
                    "subcategory": entity.subcategory,
                    "confidence_score": entity.confidence_score,
                    "offset": entity.offset,
                    "length": entity.length
                })

            return {"entities": entities}

        except Exception as e:
            logger.error(f"Azure NER error: {e}")
            raise

    async def _extract_entities_local(self, text: str) -> Dict[str, Any]:
        """Local simulation of entity extraction"""
        entities = []

        patterns = {
            "OWNER": [r'Owner[:\s]*([A-Za-z\s]+)'],
            "TENANT": [r'Tenant[:\s]*([A-Za-z\s]+)'],
            "ADDRESS": [r'Property Address[:\s]*([\w\s,]+\d{5})'],
            "PIN": [r'PIN Code[:\s]*(\S+)'],
            "MONEY": [r'\$([\d,]+)'],
            "DATE": [
                r'Start Date[:\s]*([A-Za-z]+ \d{1,2}, \d{4})',
                r'End Date[:\s]*([A-Za-z]+ \d{1,2}, \d{4})'
            ],
            "DOC_TYPE": [r'Document Type[:\s]*(.*)']
        }

        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entities.append({
                        "text": match.group(1).strip(),
                        "category": category,
                        "confidence_score": 0.95,
                        "offset": match.start(),
                        "length": len(match.group(0))
                    })

        return {"entities": entities}

    async def extract_structured_data(self, text: str) -> Dict[str, Any]:
        """Extract structured data specifically for real estate documents"""
        try:
            entities_result = await self.extract_entities(text)
            entities = entities_result.get("entities", [])

            structured_data = {
                "landlord_name": None,
                "tenant_name": None,
                "monthly_rent": None,
                "document_type": self._classify_document_type(text),
                "lease_start_date": None,
                "lease_end_date": None,
                "property_address": None,
                "pin_code": None,
                "phone_numbers": [],
                "property_details": self._extract_property_details(text),
                "security_deposit": None
            }

            for entity in entities:
                category = entity["category"]
                value = entity["text"]

                if category == "OWNER":
                    structured_data["landlord_name"] = value
                elif category == "TENANT":
                    structured_data["tenant_name"] = value
                elif category == "ADDRESS":
                    structured_data["property_address"] = value
                elif category == "PIN":
                    structured_data["pin_code"] = value
                elif category == "MONEY":
                    if not structured_data["monthly_rent"]:
                        structured_data["monthly_rent"] = value
                elif category == "DATE":
                    if not structured_data["lease_start_date"]:
                        structured_data["lease_start_date"] = value
                    else:
                        structured_data["lease_end_date"] = value
                elif category == "DOC_TYPE":
                    structured_data["document_type"] = value

            return structured_data

        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return {"error": str(e)}

    def _classify_document_type(self, text: str) -> str:
        text_lower = text.lower()
        if "lease" in text_lower or "rental" in text_lower:
            return "Rental Agreement"
        elif "sale" in text_lower or "purchase" in text_lower:
            return "Purchase Agreement"
        elif "mortgage" in text_lower:
            return "Mortgage Document"
        elif "deed" in text_lower:
            return "Deed"
        elif "inspection" in text_lower:
            return "Inspection Report"
        return "unknown"

    def _extract_property_details(self, text: str) -> Dict[str, Any]:
        details = {}
        if re.search(r'apartment|flat', text, re.IGNORECASE):
            details["property_type"] = "apartment"
        elif re.search(r'house|home', text, re.IGNORECASE):
            details["property_type"] = "house"
        elif re.search(r'condo|condominium', text, re.IGNORECASE):
            details["property_type"] = "condominium"

        if re.search(r'pet|dog|cat', text, re.IGNORECASE):
            details["pets_mentioned"] = True
        else:
            details["pets_mentioned"] = False

        return details
