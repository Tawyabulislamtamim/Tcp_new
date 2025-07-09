import os
from pathlib import Path

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    # Server configuration
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))
    
    # CORS configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001').split(',')
    
    # File transfer configuration
    DEFAULT_ALGORITHM = os.environ.get('DEFAULT_ALGORITHM', 'reno')
    CHUNK_SIZE = int(os.environ.get('CHUNK_SIZE', 8192))
    MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 1024 * 1024 * 1024))  # 1GB
    
    # Cleanup configuration
    CLEANUP_INTERVAL = int(os.environ.get('CLEANUP_INTERVAL', 60))  # seconds
    CLIENT_TIMEOUT = int(os.environ.get('CLIENT_TIMEOUT', 300))  # seconds
    
    # Directory configuration
    UPLOAD_FOLDER = Path(os.environ.get('UPLOAD_FOLDER', './uploads'))
    DOWNLOAD_FOLDER = Path(os.environ.get('DOWNLOAD_FOLDER', './downloads'))
    
    @staticmethod
    def init_app(app):
        """Initialize Flask app with configuration"""
        # Ensure required directories exist
        Config.UPLOAD_FOLDER.mkdir(exist_ok=True)
        Config.DOWNLOAD_FOLDER.mkdir(exist_ok=True)
        
        # Set Flask configuration
        app.config.from_object(Config)
        
        # Additional Flask-specific settings
        app.config['MAX_CONTENT_LENGTH'] = Config.MAX_FILE_SIZE