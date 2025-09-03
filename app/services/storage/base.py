from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
import hashlib
import os

class StorageService(ABC):
    """Abstract base class for storage services"""
    
    @abstractmethod
    def upload_file(self, file_data: BinaryIO, destination_path: str, bucket: Optional[str] = None) -> str:
        """Upload a file to storage and return the storage path"""
        pass
    
    @abstractmethod
    def download_file(self, storage_path: str, bucket: Optional[str] = None) -> BinaryIO:
        """Download a file from storage"""
        pass
    
    @abstractmethod
    def delete_file(self, storage_path: str, bucket: Optional[str] = None) -> bool:
        """Delete a file from storage"""
        pass
    
    @abstractmethod
    def get_file_url(self, storage_path: str, bucket: Optional[str] = None, signed: bool = False, 
                    expiration: int = 3600) -> str:
        """Get public URL for a file, optionally signed with expiration"""
        pass
    
    @abstractmethod
    def file_exists(self, storage_path: str, bucket: Optional[str] = None) -> bool:
        """Check if a file exists in storage"""
        pass
    
    def calculate_checksum(self, file_data: BinaryIO) -> str:
        """Calculate MD5 checksum of file data"""
        file_data.seek(0)
        hash_md5 = hashlib.md5()
        for chunk in iter(lambda: file_data.read(4096), b""):
            hash_md5.update(chunk)
        file_data.seek(0)
        return hash_md5.hexdigest()
    
    def get_file_size(self, file_data: BinaryIO) -> int:
        """Get size of file data in bytes"""
        file_data.seek(0, os.SEEK_END)
        size = file_data.tell()
        file_data.seek(0)
        return size
