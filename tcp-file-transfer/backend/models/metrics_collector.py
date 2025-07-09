import time
import threading
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class NetworkMetrics:
    timestamp: float
    cwnd: float
    ssthresh: float
    rtt: float
    bandwidth: float
    packet_loss: float
    algorithm: str
    client_id: str
    
class MetricsCollector:
    def __init__(self, max_samples=1000):
        self.metrics_history = deque(maxlen=max_samples)
        self.client_metrics = {}
        self.global_metrics = {}
        self.lock = threading.Lock()
        
    def record_metrics(self, client_id: str, metrics: NetworkMetrics):
        with self.lock:
            self.metrics_history.append(metrics)
            
            if client_id not in self.client_metrics:
                self.client_metrics[client_id] = deque(maxlen=100)
            
            self.client_metrics[client_id].append(metrics)
            self._update_global_metrics()
            
    def _update_global_metrics(self):
        if not self.metrics_history:
            return
            
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 samples
        
        self.global_metrics = {
            'total_clients': len(self.client_metrics),
            'avg_cwnd': sum(m.cwnd for m in recent_metrics) / len(recent_metrics),
            'avg_rtt': sum(m.rtt for m in recent_metrics) / len(recent_metrics),
            'total_bandwidth': sum(m.bandwidth for m in recent_metrics),
            'avg_packet_loss': sum(m.packet_loss for m in recent_metrics) / len(recent_metrics),
            'algorithm_distribution': self._get_algorithm_distribution(),
            'timestamp': time.time()
        }
        
    def get_global_metrics(self) -> Dict:
        with self.lock:
            return self.global_metrics.copy()
            
    def get_client_metrics(self, client_id: str) -> List[NetworkMetrics]:
        with self.lock:
            return list(self.client_metrics.get(client_id, []))
            
    def get_recent_metrics(self, seconds: int = 30) -> List[NetworkMetrics]:
        with self.lock:
            current_time = time.time()
            return [m for m in self.metrics_history 
                   if current_time - m.timestamp <= seconds]