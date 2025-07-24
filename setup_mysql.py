#!/usr/bin/env python3
"""
MySQL setup script for Real Estate Document Processor
"""

import os
import sys
import subprocess
from pathlib import Path
import pymysql

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

def create_mysql_database():
    """Create MySQL database if it doesn't exist"""
    try:
        # Connection parameters
        host = os.getenv('MYSQL_HOST', 'localhost')
        port = int(os.getenv('MYSQL_PORT', 3306))
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', 'password')
        database = os.getenv('MYSQL_DATABASE', 'real_estate_docs')
        
        print(f"\nConnecting to MySQL at {host}:{port}...")
        
        # Connect to MySQL server (without specifying database)
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{database}' created or already exists")
        
        # Create user if it doesn't exist (for production)
        try:
            cursor.execute(f"CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'apppassword'")
            cursor.execute(f"GRANT ALL PRIVILEGES ON {database}.* TO 'appuser'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            print("✅ Application user created with proper privileges")
        except Exception as e:
            print(f"⚠️ User creation warning (may already exist): {e}")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL database setup failed: {e}")
        print("\nPlease ensure:")
        print("1. MySQL server is running")
        print("2. Connection parameters in .env are correct")
        print("3. User has proper privileges")
        return False

def setup_environment():
    """Set up the MySQL backend environment"""
    print("Setting up Real Estate Document Processor - MySQL Backend")
    print("=" * 60)
    
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
        env_content = """# MySQL Database Configuration
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/real_estate_docs
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=password
MYSQL_DATABASE=real_estate_docs

# Local Development
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
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Install dependencies
    if not run_command("python -m pip install -r requirements.txt", "Installing dependencies"):
        print("❌ Failed to install dependencies. Please check the error above.")
        return False
    
    # Setup MySQL database
    print("\nSetting up MySQL database...")
    if not create_mysql_database():
        print("❌ MySQL setup failed. Please check your MySQL installation and configuration.")
        return False
    
    # Initialize database tables
    print("\nInitializing database tables...")
    try:
        from app.database import init_db
        init_db()
        print("✅ Database tables initialized")
    except Exception as e:
        print(f"❌ Database table initialization failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 MySQL Backend setup completed successfully!")
    print("\nNext steps:")
    print("1. Start MySQL server if not running")
    print("2. Run the server: python run_local.py")
    print("3. Open your browser to: http://localhost:8000")
    print("4. View API docs at: http://localhost:8000/docs")
    print("5. Test the API: python test_api.py")
    print("\nFor Azure integration, update the .env file with your Azure credentials.")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    setup_environment()