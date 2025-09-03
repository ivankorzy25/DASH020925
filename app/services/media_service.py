from typing import Optional, BinaryIO, List
from sqlalchemy.orm import Session
from app.models import Media, MediaVersion, MediaType, Product
from app.services.storage import get_storage_service
from app.services.audit_service import audit_log
import datetime
import os

class MediaService:
    """Service for managing media files and versions"""
    
    def __init__(self, db: Session):
        self.db = db
        self.storage = get_storage_service()
    
    def upload_media(
        self,
        file_data: BinaryIO,
        filename: str,
        media_type: MediaType,
        title: str,
        uploaded_by: str,
        product_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Media:
        """Upload a new media file and create initial version"""
        
        # Validate file size
        max_size = 100 * 1024 * 1024  # 100MB
        file_size = self.storage.get_file_size(file_data)
        if file_size > max_size:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size} bytes")
        
        # Calculate checksum
        checksum = self.storage.calculate_checksum(file_data)
        
        # Check if media with same checksum already exists
        existing_media = self.db.query(Media).filter(Media.checksum == checksum).first()
        if existing_media:
            raise ValueError("File with same content already exists")
        
        # Generate storage path
        file_ext = os.path.splitext(filename)[1]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        storage_filename = f"{timestamp}_{checksum[:8]}{file_ext}"
        storage_path = f"{media_type.value}/{storage_filename}"
        
        # Upload to storage
        final_storage_path = self.storage.upload_file(file_data, storage_path)
        
        # Get public URL
        public_url = self.storage.get_file_url(final_storage_path)
        
        # Create media record
        media = Media(
            product_id=product_id,
            type=media_type,
            title=title,
            file_name=filename,
            storage_bucket=os.getenv("STORAGE_BUCKET", "uploads"),
            storage_path=final_storage_path,
            public_url=public_url,
            size_bytes=file_size,
            checksum=checksum,
            mime_type=self._get_mime_type(filename),
            uploaded_by=uploaded_by,
            uploaded_at=datetime.datetime.now()
        )
        
        self.db.add(media)
        self.db.flush()  # Get the media ID
        
        # Create initial version
        version = MediaVersion(
            media_id=media.id,
            version=1,
            storage_path=final_storage_path,
            public_url=public_url,
            notes=notes or "Initial version",
            created_at=datetime.datetime.now()
        )
        
        self.db.add(version)
        media.current_version_id = version.id
        
        self.db.commit()
        
        # Audit log
        audit_log(
            self.db,
            entity="media",
            entity_id=media.id,
            action="create",
            payload={
                "filename": filename,
                "title": title,
                "type": media_type.value,
                "size": file_size
            },
            actor=uploaded_by
        )
        
        return media
    
    def create_new_version(
        self,
        media_id: int,
        file_data: BinaryIO,
        filename: str,
        uploaded_by: str,
        notes: Optional[str] = None
    ) -> MediaVersion:
        """Create a new version of existing media"""
        
        media = self.db.query(Media).filter(Media.id == media_id).first()
        if not media:
            raise ValueError("Media not found")
        
        # Calculate checksum and check if same as current version
        checksum = self.storage.calculate_checksum(file_data)
        if checksum == media.checksum:
            raise ValueError("New file has same content as current version")
        
        # Get current version number
        current_version = self.db.query(MediaVersion).filter(
            MediaVersion.media_id == media_id
        ).order_by(MediaVersion.version.desc()).first()
        
        new_version_number = current_version.version + 1 if current_version else 1
        
        # Generate new storage path
        file_ext = os.path.splitext(filename)[1]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        storage_filename = f"{timestamp}_{checksum[:8]}{file_ext}"
        storage_path = f"{media.type.value}/{storage_filename}"
        
        # Upload to storage
        final_storage_path = self.storage.upload_file(file_data, storage_path)
        public_url = self.storage.get_file_url(final_storage_path)
        
        # Create new version
        version = MediaVersion(
            media_id=media_id,
            version=new_version_number,
            storage_path=final_storage_path,
            public_url=public_url,
            notes=notes or f"Version {new_version_number}",
            created_at=datetime.datetime.now()
        )
        
        self.db.add(version)
        self.db.flush()
        
        # Update media record
        media.file_name = filename
        media.storage_path = final_storage_path
        media.public_url = public_url
        media.size_bytes = self.storage.get_file_size(file_data)
        media.checksum = checksum
        media.mime_type = self._get_mime_type(filename)
        media.current_version_id = version.id
        media.uploaded_at = datetime.datetime.now()
        
        self.db.commit()
        
        # Audit log
        audit_log(
            self.db,
            entity="media",
            entity_id=media_id,
            action="update",
            payload={
                "version": new_version_number,
                "filename": filename,
                "notes": notes
            },
            actor=uploaded_by
        )
        
        return version
    
    def get_media_versions(self, media_id: int) -> List[MediaVersion]:
        """Get all versions of a media file"""
        return self.db.query(MediaVersion).filter(
            MediaVersion.media_id == media_id
        ).order_by(MediaVersion.version.desc()).all()
    
    def delete_media(self, media_id: int, deleted_by: str) -> bool:
        """Delete media file and all its versions"""
        media = self.db.query(Media).filter(Media.id == media_id).first()
        if not media:
            return False
        
        # Delete from storage
        try:
            self.storage.delete_file(media.storage_path)
        except:
            pass  # Continue even if storage deletion fails
        
        # Delete versions
        versions = self.db.query(MediaVersion).filter(MediaVersion.media_id == media_id).all()
        for version in versions:
            self.db.delete(version)
        
        # Delete media
        self.db.delete(media)
        self.db.commit()
        
        # Audit log
        audit_log(
            self.db,
            entity="media",
            entity_id=media_id,
            action="delete",
            payload={
                "filename": media.file_name,
                "title": media.title
            },
            actor=deleted_by
        )
        
        return True
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type based on file extension"""
        ext = os.path.splitext(filename)[1].lower()
        mime_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp',
            '.mp4': 'video/mp4',
            '.mov': 'video/quicktime',
            '.avi': 'video/x-msvideo',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.pdf': 'application/pdf',
            '.html': 'text/html',
            '.htm': 'text/html',
        }
        return mime_map.get(ext, 'application/octet-stream')

    def get_all_media(self) -> List[Media]:
        """Get all media items with their associated products"""
        return self.db.query(Media).outerjoin(Product).order_by(Media.uploaded_at.desc()).all()
