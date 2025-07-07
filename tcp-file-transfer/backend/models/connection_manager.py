import uuid
import time
import threading
from typing import Dict, Optional
from .tcp_congestion import TCPCongestionControl
from .metrics_collector import MetricsCollector, NetworkMetrics

class ClientConnection:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.connected_at = time.time()
        self.last_activity = time.time()
        self.tcp_controller = TCPCongestionControl()
        self.transfer_stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'active_transfers': 0
        }
        
    def update_activity(self):
        self.last_activity = time.time()
        
    def is_active(self, timeout: int = 300) -> bool:
        return time.time() - self.last_activity < timeout

class ConnectionManager:
    def __init__(self, metrics_collector: MetricsCollector):
        self.clients: Dict[str, ClientConnection] = {}
        self.metrics_collector = metrics_collector
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_clients)
        self.cleanup_thread.daemon = True
        self.cleanup_thread.start()
        
    def register_client(self) -> str:
        client_id = str(uuid.uuid4())
        with self.lock:
            self.clients[client_id] = ClientConnection(client_id)
        return client_id
        
    def get_client(self, client_id: str) -> Optional[ClientConnection]:
        with self.lock:
            client = self.clients.get(client_id)
            if client:
                client.update_activity()
            return client
            
    def remove_client(self, client_id: str):
        with self.lock:
            if client_id in self.clients:
                del self.clients[client_id]
                
    def get_active_clients(self) -> Dict[str, ClientConnection]:
        with self.lock:
            return {cid: client for cid, client in self.clients.items() 
                   if client.is_active()}
                   
    def _cleanup_inactive_clients(self):
        while True:
            time.sleep(60)  # Check every minute
            with self.lock:
                inactive_clients = [cid for cid, client in self.clients.items()
                                  if not client.is_active()]
                for cid in inactive_clients:
                    del self.clients[cid]