#!/usr/bin/env python3
"""
Test script specifically for the ZOHO invoice analysis
"""

import json
from app.services.document_analyzer import DocumentAnalyzer

def test_zoho_invoice():
    """Test ZOHO invoice analysis with the actual text"""
    print("Testing ZOHO Invoice Analysis")
    print("=" * 50)
    
    zoho_invoice_text = """
    *This is a computer generated invoice and does not require a physical copy
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
    1.00 3,599.00 18% 647.82
    """
    
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze_document(zoho_invoice_text)
    
    print("Extracted Data (JSON):")
    print(json.dumps(result, indent=2))
    print()
    
    # Highlight key extracted fields
    print("Key Fields Extracted:")
    print(f"Document Type: {result.get('document_type')}")
    print(f"Invoice Number: {result.get('invoice_number')}")
    print(f"Invoice Date: {result.get('invoice_date')}")
    print(f"Due Date: {result.get('due_date')}")
    print(f"Bill To Name: {result.get('bill_to_name')}")
    print(f"Total Amount: {result.get('total_amount')}")
    print(f"Tax Amount: {result.get('tax_amount')}")
    print(f"Payment Status: {result.get('payment_status')}")
    print(f"PIN Code: {result.get('pin_code')}")
    print(f"Phone Numbers: {result.get('phone_numbers')}")
    print(f"Confidence Score: {result.get('confidence_score')}")

if __name__ == "__main__":
    test_zoho_invoice()