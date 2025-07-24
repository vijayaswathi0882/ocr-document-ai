import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class DocumentAnalyzer:
    """Intelligent document analysis system for extracting structured data"""
    
    def __init__(self):
        self.document_patterns = {
            'invoice': [
                r'invoice',
                r'tax\s+invoice',
                r'invoice#',
                r'bill\s+to',
                r'invoice\s+number',
                r'invoice\s+date',
                r'due\s+date',
                r'total\s+amount',
                r'amount\s+due',
                r'gstin',
                r'pan\s+no',
                r'payment\s+made'
            ],
            'rental_agreement': [
                r'lease\s+agreement',
                r'rental\s+agreement',
                r'landlord',
                r'tenant',
                r'monthly\s+rent',
                r'lease\s+start',
                r'lease\s+end',
                r'security\s+deposit'
            ],
            'utility_bill': [
                r'utility\s+bill',
                r'electric\s+bill',
                r'gas\s+bill',
                r'water\s+bill',
                r'service\s+period',
                r'meter\s+reading',
                r'usage'
            ]
        }
    
    def analyze_document(self, text: str) -> Dict[str, Any]:
        """
        Analyze document text and extract structured data in JSON format
        
        Args:
            text (str): Raw text from OCR or document
            
        Returns:
            Dict[str, Any]: Structured data in JSON format
        """
        try:
            # Initialize result structure
            result = {
                "document_type": self._identify_document_type(text),
                "tenant_name": self._extract_tenant_name(text),
                "landlord_name": self._extract_landlord_name(text),
                "property_address": self._extract_property_address(text),
                "lease_start_date": self._extract_lease_start_date(text),
                "lease_end_date": self._extract_lease_end_date(text),
                "monthly_rent": self._extract_monthly_rent(text),
                "security_deposit": self._extract_security_deposit(text),
                "pin_code": self._extract_pin_code(text),
                "phone_numbers": self._extract_phone_numbers(text),
                "invoice_number": self._extract_invoice_number(text),
                "invoice_date": self._extract_invoice_date(text),
                "due_date": self._extract_due_date(text),
                "bill_to_name": self._extract_bill_to_name(text),
                "bill_to_address": self._extract_bill_to_address(text),
                "total_amount": self._extract_total_amount(text),
                "tax_amount": self._extract_tax_amount(text),
                "payment_status": self._extract_payment_status(text),
                "pets_mentioned": self._check_pets_mentioned(text),
                "confidence_score": self._calculate_confidence_score(text, result)
            }
            
            # Calculate confidence score after all extractions
            result["confidence_score"] = self._calculate_confidence_score(text, result)
            
            logger.info(f"Document analysis completed with confidence: {result['confidence_score']}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing document: {e}")
            return {
                "document_type": null,
                "tenant_name": null,
                "landlord_name": null,
                "property_address": null,
                "lease_start_date": null,
                "lease_end_date": null,
                "monthly_rent": null,
                "security_deposit": null,
                "pin_code": null,
                "phone_numbers": [],
                "invoice_number": null,
                "invoice_date": null,
                "due_date": null,
                "bill_to_name": null,
                "bill_to_address": null,
                "total_amount": null,
                "tax_amount": null,
                "payment_status": null,
                "pets_mentioned": false,
                "confidence_score": 0.0
            }
    
    def _identify_document_type(self, text: str) -> Optional[str]:
        """Identify the type of document"""
        text_lower = text.lower()
        
        # Check for invoice indicators first
        if re.search(r'tax\s+invoice|invoice#|invoice\s+number', text_lower):
            return "invoice"
        
        # Score each document type
        scores = {}
        for doc_type, patterns in self.document_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text_lower))
                score += matches
            scores[doc_type] = score
        
        # Return the type with highest score, or null if no clear match
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                return best_type
        
        return null
    
    def _extract_tenant_name(self, text: str) -> Optional[str]:
        """Extract tenant name from text"""
        patterns = [
            r'tenant[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'renter[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'lessee[:\s]*([A-Za-z\s]+?)(?:\n|$|,)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and not re.search(r'\d', name):
                    return name
        
        return null
    
    def _extract_landlord_name(self, text: str) -> Optional[str]:
        """Extract landlord name from text"""
        patterns = [
            r'landlord[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'lessor[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'owner[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'property\s+owner[:\s]*([A-Za-z\s]+?)(?:\n|$|,)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and not re.search(r'\d', name):
                    return name
        
        return null
    
    def _extract_property_address(self, text: str) -> Optional[str]:
        """Extract property address from text"""
        patterns = [
            r'property\s+address[:\s]*([^\n]+)',
            r'address[:\s]*([^\n]+(?:\d{5}|\d{6}))',
            r'located\s+at[:\s]*([^\n]+)',
            r'premises[:\s]*([^\n]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                # Check if it looks like a valid address (contains numbers and letters)
                if re.search(r'\d+.*[A-Za-z]', address):
                    return address
        
        return null
    
    def _extract_lease_start_date(self, text: str) -> Optional[str]:
        """Extract lease start date from text"""
        patterns = [
            r'lease\s+start\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'start\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'commencement\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'lease\s+begins[:\s]*([A-Za-z]+ \d{1,2},? \d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return null
    
    def _extract_lease_end_date(self, text: str) -> Optional[str]:
        """Extract lease end date from text"""
        patterns = [
            r'lease\s+end\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'end\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'expiration\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'lease\s+expires[:\s]*([A-Za-z]+ \d{1,2},? \d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return null
    
    def _extract_monthly_rent(self, text: str) -> Optional[str]:
        """Extract monthly rent amount from text"""
        patterns = [
            r'monthly\s+rent[:\s]*\$?([\d,]+\.?\d*)',
            r'rent[:\s]*\$?([\d,]+\.?\d*)\s*(?:per\s+month|monthly|/month)',
            r'rental\s+amount[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return f"${amount}"
        
        return null
    
    def _extract_security_deposit(self, text: str) -> Optional[str]:
        """Extract security deposit amount from text"""
        patterns = [
            r'security\s+deposit[:\s]*\$?([\d,]+\.?\d*)',
            r'deposit[:\s]*\$?([\d,]+\.?\d*)',
            r'damage\s+deposit[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                return f"${amount}"
        
        return null
    
    def _extract_pin_code(self, text: str) -> Optional[str]:
        """Extract PIN/ZIP code from text"""
        patterns = [
            r'Pin\s+Code:\s*(\d{5,6})',
            r'pin\s+code[:\s]*(\d{5,6})',
            r'zip\s+code[:\s]*(\d{5})',
            r'postal\s+code[:\s]*(\d{5,6})',
            r'Pin\s+Code\s*:\s*(\d{5,6})',
            r'\b(\d{6})\b(?=\s*Tamil\s+Nadu|\s*India|\s*Telangana)',  # 6-digit PIN codes near location names
            r'\b(\d{5})\b(?=\s*Tamil\s+Nadu|\s*India|\s*Telangana)'   # 5-digit codes near location names
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return null
    
    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers from text"""
        patterns = [
            r'\((\d{3})\)\s*(\d{3})-(\d{4})',  # (555) 123-4567
            r'(\d{3})-(\d{3})-(\d{4})',        # 555-123-4567
            r'(\d{3})\.(\d{3})\.(\d{4})',      # 555.123.4567
            r'(\d{3})\s+(\d{3})\s+(\d{4})',    # 555 123 4567
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'  # Various formats
        ]
        
        phone_numbers = []
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) == 3:
                    phone = f"({match.group(1)}) {match.group(2)}-{match.group(3)}"
                    if phone not in phone_numbers:
                        phone_numbers.append(phone)
        
        return phone_numbers
    
    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number from text"""
        patterns = [
            r'INVOICE#\s*:\s*([A-Za-z0-9-]+)',
            r'invoice\s+(?:number|#)[:\s]*([A-Za-z0-9-]+)',
            r'invoice[:\s]*([A-Za-z0-9-]+)',
            r'bill\s+(?:number|#)[:\s]*([A-Za-z0-9-]+)',
            r'TAX\s+INVOICE[^#]*#\s*:\s*([A-Za-z0-9-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return null
    
    def _extract_invoice_date(self, text: str) -> Optional[str]:
        """Extract invoice date from text"""
        patterns = [
            r'DATE\s*:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'invoice\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'bill\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'DATE\s*:\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return null
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract due date from text"""
        patterns = [
            r'DUE\s+DATE\s*:\s*(\d{1,2}\s+[A-Za-z]+\s+\d{4})',
            r'due\s+date[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'payment\s+due[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'due\s+by[:\s]*([A-Za-z]+ \d{1,2},? \d{4})',
            r'DUE\s+DATE\s*:\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return null
    
    def _extract_bill_to_name(self, text: str) -> Optional[str]:
        """Extract bill to name from text"""
        patterns = [
            r'Bill\s+To\s*\n\s*([A-Za-z\s]+?)(?:\n|Attn:)',
            r'bill\s+to[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'billed\s+to[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'customer[:\s]*([A-Za-z\s]+?)(?:\n|$|,)',
            r'Bill\s+To[^A-Za-z]*([A-Za-z\s]+?)(?:Attn:|H\s+No\.|Address:|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and not re.search(r'\d', name):
                    return name
        
        return null
    
    def _extract_bill_to_address(self, text: str) -> Optional[str]:
        """Extract bill to address from text"""
        patterns = [
            r'Bill\s+To[^H]*H\s+No\.([^G]*?)(?:GSTIN|Telangana)',
            r'bill\s+to[:\s]*[A-Za-z\s]+\n([^\n]+(?:\d{5}|\d{6}))',
            r'billing\s+address[:\s]*([^\n]+)',
            r'customer\s+address[:\s]*([^\n]+)',
            r'Attn:[^\n]*\n([^G]*?)(?:GSTIN|$)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                address = match.group(1).strip()
                if re.search(r'\d+.*[A-Za-z]', address):
                    return address
        
        return null
    
    def _extract_total_amount(self, text: str) -> Optional[str]:
        """Extract total amount from text"""
        patterns = [
            r'Total\s+₹([\d,]+\.?\d*)',
            r'Total\s+Rs\.?\s*([\d,]+\.?\d*)',
            r'total\s+amount[:\s]*\$?([\d,]+\.?\d*)',
            r'total\s+amount[:\s]*₹([\d,]+\.?\d*)',
            r'total[:\s]*\$?([\d,]+\.?\d*)',
            r'total[:\s]*₹([\d,]+\.?\d*)',
            r'amount\s+due[:\s]*\$?([\d,]+\.?\d*)',
            r'amount\s+due[:\s]*₹([\d,]+\.?\d*)',
            r'balance\s+due[:\s]*\$?([\d,]+\.?\d*)',
            r'balance\s+due[:\s]*₹([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                # Determine currency symbol from the original text
                if '₹' in text:
                    return f"₹{amount}"
                else:
                    return f"${amount}"
        
        return null
    
    def _extract_tax_amount(self, text: str) -> Optional[str]:
        """Extract tax amount from text"""
        patterns = [
            r'IGST18\s*\(18%\)\s*([\d,]+\.?\d*)',
            r'IGST\s*\d+\s*\([^)]+\)\s*([\d,]+\.?\d*)',
            r'tax[:\s]*\$?([\d,]+\.?\d*)',
            r'tax[:\s]*₹([\d,]+\.?\d*)',
            r'sales\s+tax[:\s]*\$?([\d,]+\.?\d*)',
            r'sales\s+tax[:\s]*₹([\d,]+\.?\d*)',
            r'vat[:\s]*\$?([\d,]+\.?\d*)',
            r'vat[:\s]*₹([\d,]+\.?\d*)',
            r'GST[:\s]*₹([\d,]+\.?\d*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount = match.group(1).replace(',', '')
                # Determine currency symbol from the original text
                if '₹' in text:
                    return f"₹{amount}"
                else:
                    return f"${amount}"
        
        return null
    
    def _extract_payment_status(self, text: str) -> Optional[str]:
        """Extract payment status from text"""
        text_lower = text.lower()
        
        if re.search(r'\bpaid\b|\bpayment\s+received\b|\bcomplete\b|\bpayment\s+made\b', text_lower):
            return "paid"
        elif re.search(r'balance\s+due\s*₹?0\.00|balance\s+due\s*\$?0\.00', text_lower):
            return "paid"
        elif re.search(r'\bdue\b|\bpending\b|\bunpaid\b|\boverdue\b', text_lower):
            return "due"
        elif re.search(r'\bpartial\b|\bpartially\s+paid\b', text_lower):
            return "partial"
        
        return null
    
    def _check_pets_mentioned(self, text: str) -> bool:
        """Check if pets are mentioned in the document"""
        pet_keywords = [
            r'\bpet\b', r'\bdog\b', r'\bcat\b', r'\banimal\b',
            r'\bpuppy\b', r'\bkitten\b', r'\bpets\s+allowed\b',
            r'\bno\s+pets\b', r'\bpet\s+deposit\b', r'\bpet\s+fee\b'
        ]
        
        text_lower = text.lower()
        for keyword in pet_keywords:
            if re.search(keyword, text_lower):
                return True
        
        return False
    
    def _calculate_confidence_score(self, text: str, extracted_data: Dict[str, Any]) -> float:
        """Calculate confidence score based on extraction quality"""
        try:
            total_fields = 20  # Total number of extractable fields
            extracted_fields = 0
            
            # Count non-null extracted fields
            for key, value in extracted_data.items():
                if key == 'confidence_score':
                    continue
                if value is not null and value != [] and value != "":
                    extracted_fields += 1
            
            # Base confidence from field extraction
            field_confidence = extracted_fields / total_fields
            
            # Text quality indicators
            text_length = len(text)
            has_structure = bool(re.search(r'[:\n]', text))
            has_numbers = bool(re.search(r'\d', text))
            has_currency = bool(re.search(r'\$', text))
            
            # Quality multipliers
            quality_score = 1.0
            if text_length > 100:
                quality_score += 0.1
            if has_structure:
                quality_score += 0.1
            if has_numbers:
                quality_score += 0.1
            if has_currency:
                quality_score += 0.1
            
            # Final confidence calculation
            confidence = min(field_confidence * quality_score, 1.0)
            return round(confidence, 2)
            
        except Exception as e:
            logger.error(f"Error calculating confidence score: {e}")
            return 0.0