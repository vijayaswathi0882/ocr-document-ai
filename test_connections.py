#!/usr/bin/env python3
"""
Test script to verify Azure and MySQL connections
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_azure_services():
    """Test Azure service connections"""
    print("🔍 Testing Azure Services...")
    
    try:
        # Test Azure Storage
        from azure.storage.blob import BlobServiceClient
        storage_conn = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        if storage_conn:
            blob_client = BlobServiceClient.from_connection_string(storage_conn)
            # Try to list containers (this will test the connection)
            containers = list(blob_client.list_containers())
            print("✅ Azure Blob Storage: Connected successfully")
        else:
            print("❌ Azure Blob Storage: No connection string found")
    except Exception as e:
        print(f"❌ Azure Blob Storage: {e}")
    
    try:
        # Test Azure Form Recognizer
        from azure.ai.formrecognizer import DocumentAnalysisClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv('AZURE_COGNITIVE_SERVICES_ENDPOINT')
        key = os.getenv('AZURE_COGNITIVE_SERVICES_KEY')
        
        if endpoint and key:
            client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(key))
            print("✅ Azure Form Recognizer: Client initialized successfully")
        else:
            print("❌ Azure Form Recognizer: Missing endpoint or key")
    except Exception as e:
        print(f"❌ Azure Form Recognizer: {e}")
    
    try:
        # Test Azure Text Analytics
        from azure.ai.textanalytics import TextAnalyticsClient
        from azure.core.credentials import AzureKeyCredential
        
        endpoint = os.getenv('AZURE_TEXT_ANALYTICS_ENDPOINT')
        key = os.getenv('AZURE_TEXT_ANALYTICS_KEY')
        
        if endpoint and key:
            client = TextAnalyticsClient(endpoint=endpoint, credential=AzureKeyCredential(key))
            # Test with a simple text
            test_text = ["This is a test document for real estate processing."]
            result = client.recognize_entities(documents=test_text)
            print("✅ Azure Text Analytics: Connected and working")
        else:
            print("❌ Azure Text Analytics: Missing endpoint or key")
    except Exception as e:
        print(f"❌ Azure Text Analytics: {e}")

def test_mysql_connection():
    """Test MySQL database connection"""
    print("\n🔍 Testing MySQL Database...")
    
    try:
        import pymysql
        
        connection = pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT')),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DATABASE'),
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"✅ MySQL Database: Connected successfully (Version: {version[0]})")
        
        # Test if our table exists
        cursor.execute("SHOW TABLES LIKE 'documents'")
        table_exists = cursor.fetchone()
        if table_exists:
            print("✅ Documents table: Exists")
        else:
            print("⚠️ Documents table: Not found (will be created on first run)")
        
        cursor.close()
        connection.close()
        
    except Exception as e:
        print(f"❌ MySQL Database: {e}")

async def test_document_processing():
    """Test the document processing pipeline"""
    print("\n🔍 Testing Document Processing Pipeline...")
    
    try:
        # Import our services
        from app.services.ocr_service import OCRService
        from app.services.nlp_service import NLPService
        from app.services.storage_service import StorageService
        from app.services.document_processor import DocumentProcessor
        
        # Initialize services
        ocr_service = OCRService()
        nlp_service = NLPService()
        storage_service = StorageService()
        document_processor = DocumentProcessor(ocr_service, nlp_service, storage_service)
        
        print("✅ All services initialized successfully")
        
        # Create a test document
        test_content = """
        REAL ESTATE LEASE AGREEMENT
        
        Property Address: 123 Main Street, Test City, TC 12345
        
        Landlord: John Smith
        Phone: (555) 123-4567
        
        Tenant: Jane Doe
        Phone: (555) 987-6543
        
        Monthly Rent: $1,500.00
        Security Deposit: $1,500.00
        Lease Start Date: January 1, 2024
        Lease End Date: December 31, 2024
        
        Property Details:
        Type: Apartment
        Bedrooms: 2
        Bathrooms: 1
        Square Footage: 900 sq ft
        """
        
        # Create test file
        test_file = Path("test_document.txt")
        test_file.write_text(test_content)
        
        # Process the document
        result = await document_processor.process_document(str(test_file))
        
        if result.get('status') == 'success':
            print("✅ Document processing: Successful")
            print(f"   - Extracted {len(result.get('raw_text', ''))} characters")
            print(f"   - Confidence score: {result.get('confidence_score', 0)}")
            
            extracted_data = result.get('extracted_data', {})
            if extracted_data:
                print("   - Extracted fields:")
                for key, value in extracted_data.items():
                    if value and key != 'property_details':
                        print(f"     • {key}: {value}")
        else:
            print(f"❌ Document processing: Failed - {result.get('error', 'Unknown error')}")
        
        # Clean up
        if test_file.exists():
            test_file.unlink()
            
    except Exception as e:
        print(f"❌ Document processing: {e}")

async def main():
    """Main test function"""
    print("=" * 60)
    print("Real Estate Document Processor - Connection Tests")
    print("=" * 60)
    
    # Test Azure services
    await test_azure_services()
    
    # Test MySQL
    test_mysql_connection()
    
    # Test document processing
    await test_document_processing()
    
    print("\n" + "=" * 60)
    print("🎉 Connection testing completed!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())