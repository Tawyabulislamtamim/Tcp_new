import uuid
import time
import threading
from typing import Dict, Optional
from .adaptive_tcp_congestion import AdaptiveTCPCongestionControl, AlgorithmType

class NetworkMetrics:
    def __init__(self):
        self.throughput = 0
        self.latency = 0
        self.packet_loss = 0
        self.timestamp = time.time()

class MetricsCollector:
    def __init__(self):
        self.metrics = {}
        
    def record_metric(self, client_id: str, metric_type: str, value: float):
        if client_id not in self.metrics:
            self.metrics[client_id] = {}
        self.metrics[client_id][metric_type] = value

class ClientConnection:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.connected_at = time.time()
        self.last_activity = time.time()
        
        # Use the new adaptive TCP congestion control
        self.tcp_controller = AdaptiveTCPCongestionControl(AlgorithmType.RENO)
        
        self.transfer_stats = {
            'bytes_sent': 0,
            'bytes_received': 0,
            'active_transfers': 0
        }
        
    def update_activity(self):
        self.last_activity = time.time()
        
    def is_active(self, timeout: int = 300) -> bool:
        return time.time() - self.last_activity < timeout
    
    def simulate_network_activity(self):
        """Simulate network activity to trigger adaptive algorithm switching"""
        import random
        
        # Simulate varying network conditions
        base_rtt = random.uniform(10, 150)  # 10-150ms RTT
        base_bandwidth = random.uniform(100000, 10000000)  # 100KB - 10MB/s
        
        # Add some realistic network variation
        rtt_variation = random.uniform(0.8, 1.2)
        bw_variation = random.uniform(0.7, 1.3)
        
        rtt = base_rtt * rtt_variation
        bandwidth = base_bandwidth * bw_variation
        
        # Occasionally simulate packet loss
        if random.random() < 0.05:  # 5% chance
            self.tcp_controller.on_loss_detected()
        
        # Send ACK with network conditions
        ack_num = random.randint(1, 1000)
        self.tcp_controller.on_ack_received(ack_num, rtt=rtt, bandwidth=bandwidth)
        
        return rtt, bandwidth

class ConnectionManager:
    def __init__(self, metrics_collector: MetricsCollector):
        self.clients: Dict[str, ClientConnection] = {}
        self.metrics_collector = metrics_collector
        self.lock = threading.Lock()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_inactive_clients_loop)
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
                   
    def _cleanup_inactive_clients_loop(self):
        """Background thread to clean up inactive clients"""
        while True:
            time.sleep(60)  # Check every minute
            try:
                self.cleanup_inactive_clients()
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
    
    def cleanup_inactive_clients(self) -> int:
        """Clean up inactive clients and return count removed"""
        with self.lock:
            inactive_clients = [cid for cid, client in self.clients.items()
                              if not client.is_active()]
            for cid in inactive_clients:
                del self.clients[cid]
            return len(inactive_clients)