#!/usr/bin/env python3
"""
Local development server for Real Estate Document Processor
"""

import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI
import shutil
import uvicorn

# Clear Python cache to avoid import issues
for path in ["__pycache__", "app/__pycache__"]:
    if os.path.exists(path):
        shutil.rmtree(path)

# Add app to path
sys.path.append(str(Path(__file__).parent))

# Import the FastAPI app
try:
    from app.main import app
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create necessary directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("logs", exist_ok=True)

if __name__ == "__main__":
    print("=" * 60)
    print("Real Estate Document Processor - Local Development Server")
    print("=" * 60)
    print("Starting server on http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("=" * 60)

    # Run the FastAPI server
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
