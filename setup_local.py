#!/usr/bin/env python3
"""
Setup script for local development environment
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def setup_environment():
    """Set up the local development environment"""
    print("Setting up Real Estate Document Processor - Local Development Environment")
    print("=" * 70)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {python_version.major}.{python_version.minor} detected")
    
    # Create necessary directories
    print("\nCreating directories...")
    directories = ["uploads", "logs", "app/services", "app/models", "app/schemas"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("\nCreating .env file...")
        env_content = """# Local Development Configuration
DATABASE_URL=sqlite:///./local_database.db
LOCAL_UPLOAD_PATH=./uploads
SECRET_KEY=your-secret-key-for-development
ENVIRONMENT=development

# Azure Configuration (Optional for local development)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_COGNITIVE_SERVICES_ENDPOINT=
AZURE_COGNITIVE_SERVICES_KEY=
AZURE_TEXT_ANALYTICS_ENDPOINT=
AZURE_TEXT_ANALYTICS_KEY=
"""
        env_file.write_text(env_content)
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")
    
    # Install dependencies
    if not run_command("python -m pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check the error above.")
        return False
    
    # Initialize database
    print("\nInitializing database...")
    try:
        from app.database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the server: python run_local.py")
    print("2. Open your browser to: http://localhost:8000")
    print("3. View API docs at: http://localhost:8000/docs")
    print("4. Test the API: python test_api.py")
    print("\nFor Azure integration, update the .env file with your Azure credentials.")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    setup_environment()