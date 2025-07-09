import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class FileInfo:
    name: str
    path: str
    size: int
    is_directory: bool
    modified_time: float
    mime_type: str

class FileManager:
    def __init__(self, root_directory: str = './shared_files'):
        self.root = Path(root_directory).resolve()
        os.makedirs(self.root, exist_ok=True)
    
    def _validate_path(self, path: str) -> Path:
        """Resolve and validate a path is within the root directory"""
        full_path = (self.root / path).resolve()
        if not str(full_path).startswith(str(self.root)):
            raise ValueError("Path traversal attempt detected")
        return full_path
    
    def get_file_path(self, path: str) -> Optional[Path]:
        """Get validated Path object for a file"""
        try:
            full_path = self._validate_path(path)
            if full_path.exists():
                return full_path
            return None
        except ValueError:
            return None
    
    def get_file_info(self, path: str) -> Optional[FileInfo]:
        """Get information about a file/directory"""
        full_path = self.get_file_path(path)
        if not full_path:
            return None
            
        stat = full_path.stat()
        return FileInfo(
            name=full_path.name,
            path=str(full_path.relative_to(self.root)),
            size=stat.st_size,
            is_directory=full_path.is_dir(),
            modified_time=stat.st_mtime,
            mime_type=self._get_mime_type(full_path)
        )
    
    def list_directory(self, path: str = '') -> List[FileInfo]:
        """List contents of a directory"""
        full_path = self._validate_path(path)
        if not full_path.is_dir():
            raise ValueError("Path is not a directory")
            
        return [
            self.get_file_info(str(item.relative_to(self.root)))
            for item in sorted(full_path.iterdir())
        ]
    
    def _get_mime_type(self, path: Path) -> str:
        """Simple MIME type detection"""
        if path.is_dir():
            return 'inode/directory'
        
        ext = path.suffix.lower()
        if ext in ('.jpg', '.jpeg', '.png', '.gif'):
            return f'image/{ext[1:]}'
        if ext == '.pdf':
            return 'application/pdf'
        if ext in ('.txt', '.csv', '.json'):
            return f'text/{ext[1:]}'
        return 'application/octet-stream'