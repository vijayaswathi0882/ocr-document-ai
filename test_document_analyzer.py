#!/usr/bin/env python3
"""
Test script for the Document Analyzer system
"""

import json
from app.services.document_analyzer import DocumentAnalyzer

def test_rental_agreement():
    """Test rental agreement analysis"""
    print("Testing Rental Agreement Analysis")
    print("=" * 50)
    
    sample_rental_text = """
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
    """
    
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze_document(sample_rental_text)
    
    print("Extracted Data (JSON):")
    print(json.dumps(result, indent=2))
    print()

def test_invoice():
    """Test invoice analysis"""
    print("Testing Invoice Analysis")
    print("=" * 50)
    
    sample_invoice_text = """
    INVOICE
    
    Invoice Number: INV-2024-001
    Invoice Date: March 15, 2024
    Due Date: April 15, 2024
    
    Bill To:
    ABC Company
    456 Business Ave
    Corporate City, CC 54321
    
    Description: Professional Services
    Amount: $2,500.00
    Tax: $250.00
    Total Amount: $2,750.00
    
    Payment Status: Due
    """
    
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze_document(sample_invoice_text)
    
    print("Extracted Data (JSON):")
    print(json.dumps(result, indent=2))
    print()

def test_utility_bill():
    """Test utility bill analysis"""
    print("Testing Utility Bill Analysis")
    print("=" * 50)
    
    sample_utility_text = """
    ELECTRIC UTILITY BILL
    
    Account Number: 123456789
    Service Address: 789 Power Street, Electric City, EC 98765
    Bill Date: March 1, 2024
    Due Date: March 25, 2024
    
    Customer: Mary Johnson
    Phone: (555) 444-3333
    
    Service Period: February 1 - February 29, 2024
    Usage: 850 kWh
    
    Charges:
    Electricity: $127.50
    Delivery: $22.50
    Tax: $15.00
    Total Amount: $165.00
    
    Payment Status: Paid
    """
    
    analyzer = DocumentAnalyzer()
    result = analyzer.analyze_document(sample_utility_text)
    
    print("Extracted Data (JSON):")
    print(json.dumps(result, indent=2))
    print()

def main():
    """Run all tests"""
    print("Document Analyzer Test Suite")
    print("=" * 60)
    
    test_rental_agreement()
    test_invoice()
    test_utility_bill()
    
    print("=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    main()