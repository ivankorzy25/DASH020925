from app.services.storage.local import LocalStorageService
from app.services.storage.base import StorageService
import os

def get_storage_service() -> StorageService:
    """Factory function to get the appropriate storage service based on configuration"""
    storage_type = os.getenv("STORAGE_TYPE", "local")
    
    if storage_type == "local":
        base_path = os.getenv("STORAGE_LOCAL_PATH", "./storage")
        base_url = os.getenv("STORAGE_LOCAL_URL", "/storage/")
        return LocalStorageService(base_path, base_url)
    
    elif storage_type == "gcs":
        # GCS implementation will be added in future iteration
        raise NotImplementedError("GCS storage not yet implemented")
    
    elif storage_type == "s3":
        # S3 implementation will be added in future iteration
        raise NotImplementedError("S3 storage not yet implemented")
    
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
