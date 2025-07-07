import os

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload size
    
    # File storage
    UPLOAD_FOLDER = './shared_files'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # TCP settings
    DEFAULT_CONGESTION_ALGORITHM = 'reno'  # reno, tahoe, cubic
    INITIAL_CWND = 1
    INITIAL_SSTHRESH = 65535
    
    # Metrics
    METRICS_HISTORY_SIZE = 1000
    METRICS_UPDATE_INTERVAL = 0.5  # seconds
    
    # Network simulation (for testing)
    SIMULATE_NETWORK = False
    SIMULATED_RTT = 0.05  # seconds
    SIMULATED_PACKET_LOSS = 0.01  # 1% packet loss