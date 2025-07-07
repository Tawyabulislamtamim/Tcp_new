import os
import mimetypes
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class FileInfo:
    name: str
    path: str
    size: int
    is_directory: bool
    modified_time: float
    mime_type: Optional[str] = None
    
class FileManager:
    def __init__(self, base_directory: str = "./shared_files"):
        self.base_directory = Path(base_directory).resolve()
        self.base_directory.mkdir(exist_ok=True)
        
    def list_directory(self, relative_path: str = "") -> List[FileInfo]:
        try:
            target_path = self.base_directory / relative_path
            
            # Security check - prevent directory traversal
            if not str(target_path.resolve()).startswith(str(self.base_directory)):
                raise ValueError("Invalid path")
                
            if not target_path.exists() or not target_path.is_dir():
                return []
                
            files = []
            for item in target_path.iterdir():
                try:
                    stat = item.stat()
                    mime_type = None if item.is_dir() else mimetypes.guess_type(str(item))[0]
                    
                    files.append(FileInfo(
                        name=item.name,
                        path=str(item.relative_to(self.base_directory)),
                        size=stat.st_size,
                        is_directory=item.is_dir(),
                        modified_time=stat.st_mtime,
                        mime_type=mime_type
                    ))
                except (OSError, ValueError):
                    continue
                    
            return sorted(files, key=lambda f: (not f.is_directory, f.name.lower()))
            
        except Exception as e:
            print(f"Error listing directory: {e}")
            return []
            
    def get_file_info(self, relative_path: str) -> Optional[FileInfo]:
        try:
            target_path = self.base_directory / relative_path
            
            if not str(target_path.resolve()).startswith(str(self.base_directory)):
                return None
                
            if not target_path.exists():
                return None
                
            stat = target_path.stat()
            mime_type = None if target_path.is_dir() else mimetypes.guess_type(str(target_path))[0]
            
            return FileInfo(
                name=target_path.name,
                path=relative_path,
                size=stat.st_size,
                is_directory=target_path.is_dir(),
                modified_time=stat.st_mtime,
                mime_type=mime_type
            )
            
        except Exception:
            return None
            
    def get_file_path(self, relative_path: str) -> Optional[Path]:
        try:
            target_path = self.base_directory / relative_path
            
            if not str(target_path.resolve()).startswith(str(self.base_directory)):
                return None
                
            if target_path.exists() and target_path.is_file():
                return target_path
                
        except Exception:
            pass
            
        return None