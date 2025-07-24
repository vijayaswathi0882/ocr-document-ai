import os
import shutil
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

from app.config import get_settings

logger = logging.getLogger(__name__)

class StorageService:
    """Service for file storage using Azure Blob Storage"""
    
    def __init__(self):
        self.settings = get_settings()
        self.blob_service_client = None
        
        if AZURE_AVAILABLE and self.settings.azure_storage_connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(
                    self.settings.azure_storage_connection_string
                )
                logger.info("Azure Blob Storage client initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Azure Blob Storage client: {e}")
                self.blob_service_client = None
        
        if not self.blob_service_client:
            logger.info("Using local file storage")
            # Create local upload directory
            os.makedirs(self.settings.local_upload_path, exist_ok=True)
    
    async def upload_file(self, file_path: str, blob_name: str) -> Dict[str, Any]:
        """Upload file to storage"""
        try:
            if self.blob_service_client:
                return await self._upload_to_azure(file_path, blob_name)
            else:
                return await self._upload_to_local(file_path, blob_name)
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return {"success": False, "error": str(e)}
    
    async def _upload_to_azure(self, file_path: str, blob_name: str) -> Dict[str, Any]:
        """Upload file to Azure Blob Storage"""
        try:
            container_name = "real-estate-documents"
            
            # Create container if it doesn't exist
            container_client = self.blob_service_client.get_container_client(container_name)
            try:
                container_client.create_container()
            except Exception:
                pass  # Container might already exist
            
            # Upload file
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
            
            return {
                "success": True,
                "url": blob_client.url,
                "container": container_name,
                "blob_name": blob_name
            }
            
        except Exception as e:
            logger.error(f"Azure upload error: {e}")
            raise
    
    async def _upload_to_local(self, file_path: str, blob_name: str) -> Dict[str, Any]:
        """Upload file to local storage"""
        try:
            destination_path = os.path.join(self.settings.local_upload_path, blob_name)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(destination_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, destination_path)
            
            return {
                "success": True,
                "path": destination_path,
                "blob_name": blob_name
            }
            
        except Exception as e:
            logger.error(f"Local upload error: {e}")
            raise
    
    async def download_file(self, blob_name: str, download_path: str) -> Dict[str, Any]:
        """Download file from storage"""
        try:
            if self.blob_service_client:
                return await self._download_from_azure(blob_name, download_path)
            else:
                return await self._download_from_local(blob_name, download_path)
        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            return {"success": False, "error": str(e)}
    
    async def _download_from_azure(self, blob_name: str, download_path: str) -> Dict[str, Any]:
        """Download file from Azure Blob Storage"""
        try:
            container_name = "real-estate-documents"
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            with open(download_path, "wb") as download_file:
                download_file.write(blob_client.download_blob().readall())
            
            return {
                "success": True,
                "path": download_path
            }
            
        except Exception as e:
            logger.error(f"Azure download error: {e}")
            raise
    
    async def _download_from_local(self, blob_name: str, download_path: str) -> Dict[str, Any]:
        """Download file from local storage"""
        try:
            source_path = os.path.join(self.settings.local_upload_path, blob_name)
            
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"File not found: {source_path}")
            
            shutil.copy2(source_path, download_path)
            
            return {
                "success": True,
                "path": download_path
            }
            
        except Exception as e:
            logger.error(f"Local download error: {e}")
            raise
    
    async def delete_file(self, blob_name: str) -> Dict[str, Any]:
        """Delete file from storage"""
        try:
            if self.blob_service_client:
                return await self._delete_from_azure(blob_name)
            else:
                return await self._delete_from_local(blob_name)
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return {"success": False, "error": str(e)}
    
    async def _delete_from_azure(self, blob_name: str) -> Dict[str, Any]:
        """Delete file from Azure Blob Storage"""
        try:
            container_name = "real-estate-documents"
            blob_client = self.blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )
            
            blob_client.delete_blob()
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Azure delete error: {e}")
            raise
    
    async def _delete_from_local(self, blob_name: str) -> Dict[str, Any]:
        """Delete file from local storage"""
        try:
            file_path = os.path.join(self.settings.local_upload_path, blob_name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            return {"success": True}
            
        except Exception as e:
            logger.error(f"Local delete error: {e}")
            raise