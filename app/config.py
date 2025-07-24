from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE")

class Settings(BaseSettings):
    """Application configuration"""
    
    # Azure Configuration
    azure_storage_connection_string: str = ""
    azure_cognitive_services_endpoint: str = ""
    azure_cognitive_services_key: str = ""
    azure_text_analytics_endpoint: str = ""
    azure_text_analytics_key: str = ""
    
    # MySQL Database Configuration
    database_url: str = "mysql+pymysql://root:password@localhost:3306/real_estate_docs"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "password"
    mysql_database: str = "real_estate_docs"
    
    # Local Development
    local_upload_path: str = "./uploads"
    
    # Security
    secret_key: str = "your-secret-key-here"
    environment: str = "development"
    
    # Processing Configuration
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_formats: list = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff']
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()