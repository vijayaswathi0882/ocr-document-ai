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
@router.get("/test-zoho-invoice")
async def test_zoho_invoice_endpoint():
    """
    Test endpoint with the actual ZOHO invoice text for debugging
    """
    zoho_text = """*This is a computer generated invoice and does not require a physical copy
 1
 Sub Total 3,599.00
 IGST18 (18%) 647.82
 Total ₹4,246.82
 Payment Made (-) 4,246.82
 Balance Due ₹0.00
 ZOHO Corporation Private Limited
 Authorized Signatory
 Total In Words
 Rupees Four Thousand Two Hundred Forty-Six and Eighty-Two Paise 
Only
 Notes
 This payment was charged from the credit card ending with 8992
 ZOHO Corporation Private Limited
 942, Krisp IT Park, Vandalur Kelambakkam Road,
 Kizhakottaiyur Village, Vandalur Taluk,
 Chennai, Chengalpattu,
 Pin Code: 600127
 Tamil Nadu, India
 Phone: +91 4469656278
 Pan No: AAACZ4322M
 CIN:  U40100TN2010PTC075961
 Tan No: CHEZ03229C
 GSTIN: 33AAACZ4322M2Z9
 TAX INVOICE
  INVOICE# : 1025260110273
  DATE : 12 Jun 2025
  TERMS : Due on Receipt
  DUE DATE : 12 Jun 2025
 P.O.# : 277000485847392
  Name Of State : Telangana (36)
  License Order No : RPIN277000376146746
  License Sent to : procurex Technologies Pvt 
LTD
  UserMail : bharath.
 devaram@procurextech.com
 Place Of Supply : Hyderabad
 Bill To Ship To
 procurex Technologies Pvt LTD
 Attn: bharath.devaram@procurextech.com
 H No.4-49/2,Vattinagulapally, Sy.No. 237 Nearby Landmark: Rendez , 
Gandipet Hyderabad 500019
 Telangana India
 GSTIN 36AAOCP7271P1ZG
 procurex Technologies Pvt LTD
 H No.4-49/2,Vattinagulapally, Sy.No. 237 Nearby Landmark: Rendez , 
Gandipet Hyderabad 500019
 Telangana India
 Item & Description Qty Rate
 IGST
 Amount % Amt
 310572SM
 Service : Zoho Books
 Plan : Premium
 Payment Duration : Monthly
 Org Name : Procurex Technologies
 Start 11 June 2025 End 10 July 2025
 SAC: 997331
 1.00 3,599.00 18% 647.82"""
    
    try:
        analyzer = DocumentAnalyzer()
        result = analyzer.analyze_document(zoho_text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")