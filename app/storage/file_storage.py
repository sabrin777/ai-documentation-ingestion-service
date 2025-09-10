import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import Dict, Any
import uuid


class FileStorage:
    """File storage service for handling uploaded files"""
    
    def __init__(self, storage_root: str = "/app/storage"):
        """Initialize file storage with root directory"""
        self.storage_root = Path(storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
    
    def store_file(self, temp_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Store a temporary file permanently and return file information
        
        Args:
            temp_path: Path to the temporary file
            original_filename: Original filename from upload
            
        Returns:
            Dictionary with file information including:
            - stored_path: Path where file is stored
            - stored_filename: Generated filename for storage
            - original_filename: Original filename
            - mime_type: MIME type of the file
            - file_size: Size in bytes
            - content_hash: SHA256 hash of file content
        """
        if not os.path.exists(temp_path):
            raise FileNotFoundError(f"Temporary file not found: {temp_path}")
        
        # Generate unique filename to avoid conflicts
        file_extension = Path(original_filename).suffix
        stored_filename = f"{uuid.uuid4()}{file_extension}"
        stored_path = self.storage_root / stored_filename
        
        # Copy file to permanent storage
        shutil.copy2(temp_path, stored_path)
        
        # Get file information
        file_size = stored_path.stat().st_size
        mime_type = mimetypes.guess_type(original_filename)[0]
        
        # Calculate content hash
        content_hash = self._calculate_hash(stored_path)
        
        return {
            "stored_path": str(stored_path),
            "stored_filename": stored_filename,
            "original_filename": original_filename,
            "mime_type": mime_type,
            "file_size": file_size,
            "content_hash": content_hash
        }
    
    def get_file_path(self, stored_filename: str) -> str:
        """Get the full path to a stored file"""
        return str(self.storage_root / stored_filename)
    
    def delete_file(self, stored_filename: str) -> bool:
        """Delete a stored file"""
        file_path = self.storage_root / stored_filename
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def file_exists(self, stored_filename: str) -> bool:
        """Check if a stored file exists"""
        file_path = self.storage_root / stored_filename
        return file_path.exists()
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()


# Global instance
file_storage = FileStorage()