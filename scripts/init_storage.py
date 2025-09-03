#!/usr/bin/env python3
import os
from app.services.storage import get_storage_service

def init_storage():
    """Initialize storage directories"""
    storage = get_storage_service()
    print("Storage service initialized successfully")
    
    # Create directories for each media type
    media_types = ["image", "video", "audio", "pdf", "html", "other"]
    for media_type in media_types:
        # This will create directories when first file is uploaded
        print(f"Ready for {media_type} storage")
    
    print("Storage initialization completed")

if __name__ == "__main__":
    init_storage()
