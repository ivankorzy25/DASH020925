import os
import shutil
from typing import BinaryIO, Optional
from urllib.parse import urljoin
from app.services.storage.base import StorageService

class LocalStorageService(StorageService):
    """Local filesystem storage implementation"""
    
    def __init__(self, base_path: str, base_url: str = "/storage/"):
        self.base_path = base_path
        self.base_url = base_url
        os.makedirs(base_path, exist_ok=True)
    
    def upload_file(self, file_data: BinaryIO, destination_path: str, bucket: Optional[str] = None) -> str:
        full_path = self._get_full_path(destination_path, bucket)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'wb') as f:
            shutil.copyfileobj(file_data, f)
        
        return destination_path
    
    def download_file(self, storage_path: str, bucket: Optional[str] = None) -> BinaryIO:
        full_path = self._get_full_path(storage_path, bucket)
        return open(full_path, 'rb')
    
    def delete_file(self, storage_path: str, bucket: Optional[str] = None) -> bool:
        full_path = self._get_full_path(storage_path, bucket)
        try:
            os.remove(full_path)
            return True
        except FileNotFoundError:
            return False
    
    def get_file_url(self, storage_path: str, bucket: Optional[str] = None, signed: bool = False, 
                    expiration: int = 3600) -> str:
        return urljoin(self.base_url, storage_path)
    
    def file_exists(self, storage_path: str, bucket: Optional[str] = None) -> bool:
        full_path = self._get_full_path(storage_path, bucket)
        return os.path.exists(full_path)
    
    def _get_full_path(self, storage_path: str, bucket: Optional[str] = None) -> str:
        if bucket:
            return os.path.join(self.base_path, bucket, storage_path)
        return os.path.join(self.base_path, storage_path)
