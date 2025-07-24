#!/usr/bin/env python3
"""
Test script for the Real Estate Document Processor API
"""

import requests
import json
import time
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000"
UPLOAD_URL = f"{BASE_URL}/documents/upload"
DOCUMENTS_URL = f"{BASE_URL}/documents"

def test_api():
    """Test the API endpoints"""
    print("Testing Real Estate Document Processor API")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    
    # Test 2: Create a sample document file
    print("2. Creating sample document...")
    sample_content = """
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
    
    # Create sample file
    sample_file = Path("sample_lease.txt")
    sample_file.write_text(sample_content)
    
    try:
        # Test 3: Upload document
        print("3. Uploading document...")
        with open(sample_file, 'rb') as f:
            files = {'file': (sample_file.name, f, 'text/plain')}
            response = requests.post(UPLOAD_URL, files=files)
        
        print(f"Upload Status: {response.status_code}")
        if response.status_code == 200:
            upload_result = response.json()
            document_id = upload_result.get('id')
            print(f"Document ID: {document_id}")
            print(f"Status: {upload_result.get('status')}")
            print()
            
            # Test 4: Wait for processing and check status
            print("4. Waiting for processing...")
            max_attempts = 30
            for attempt in range(max_attempts):
                response = requests.get(f"{DOCUMENTS_URL}/{document_id}")
                if response.status_code == 200:
                    doc_result = response.json()
                    status = doc_result.get('status')
                    print(f"Attempt {attempt + 1}: Status = {status}")
                    
                    if status == 'completed':
                        print("\n✅ Processing completed!")
                        print(f"Extracted Data: {json.dumps(doc_result.get('extracted_data', {}), indent=2)}")
                        print(f"Confidence Score: {doc_result.get('confidence_score', 0)}")
                        break
                    elif status == 'failed':
                        print(f"\n❌ Processing failed: {doc_result.get('error_message', 'Unknown error')}")
                        break
                    
                    time.sleep(2)
                else:
                    print(f"Error checking status: {response.status_code}")
                    break
            print()
            
            # Test 5: List all documents
            print("5. Listing all documents...")
            response = requests.get(DOCUMENTS_URL)
            if response.status_code == 200:
                documents = response.json()
                print(f"Found {len(documents)} documents")
                for doc in documents:
                    print(f"- {doc.get('filename')} ({doc.get('status')})")
            print()
            
            # Test 6: Search within document
            print("6. Testing search...")
            search_response = requests.get(f"{DOCUMENTS_URL}/{document_id}/search?query=rent")
            if search_response.status_code == 200:
                search_result = search_response.json()
                print(f"Search results: {json.dumps(search_result, indent=2)}")
            print()
            
            # Test 7: Analytics
            print("7. Getting analytics...")
            analytics_response = requests.get(f"{BASE_URL}/analytics/summary")
            if analytics_response.status_code == 200:
                analytics = analytics_response.json()
                print(f"Analytics: {json.dumps(analytics, indent=2)}")
            
        else:
            print(f"Upload failed: {response.text}")
    
    finally:
        # Clean up
        if sample_file.exists():
            sample_file.unlink()
    
    print("\n" + "=" * 50)
    print("API testing completed!")

if __name__ == "__main__":
    test_api()