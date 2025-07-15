import threading  # <-- THIS IS THE CRUCIAL IMPORT
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import defaultdict, deque

@dataclass
class NetworkMetrics:
    timestamp: float
    cwnd: float
    ssthresh: float
    rtt: float
    bandwidth: float  # in bytes/sec
    packet_loss: float
    algorithm: str
    client_id: str

class MetricsCollector:
    def __init__(self, max_history_seconds: int = 300):
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.max_history_seconds = max_history_seconds
        self.global_metrics = {
            'total_bytes_transferred': 0,
            'active_connections': 0,
            'average_rtt': 0,
            'total_packet_loss': 0
        }
        self.lock = threading.Lock()
    
    def record_metrics(self, client_id: str, metrics: NetworkMetrics):
        """Store metrics for a client"""
        with self.lock:
            # Store client metrics
            self.metrics_history[client_id].append(metrics)
            
            # Update global metrics with real transfer data
            transfer_bytes = getattr(metrics, 'bytes_transferred', 0)
            if transfer_bytes > 0:
                # This is actual transfer data, not just bandwidth estimation
                self.global_metrics['total_bytes_transferred'] += transfer_bytes
            else:
                # Fallback to bandwidth estimation for demo data
                self.global_metrics['total_bytes_transferred'] += metrics.bandwidth * 0.5  # Assuming 0.5s interval
            
            self.global_metrics['average_rtt'] = (
                self.global_metrics['average_rtt'] * 0.9 + metrics.rtt * 0.1
            )
            self.global_metrics['total_packet_loss'] += metrics.packet_loss
    
    def get_client_metrics(self, client_id: str) -> List[NetworkMetrics]:
        """Get all metrics for a specific client"""
        return list(self.metrics_history.get(client_id, []))
    
    def get_recent_metrics(self, seconds: int = 30) -> List[NetworkMetrics]:
        """Get metrics from all clients for the last N seconds"""
        now = time.time()
        recent_metrics = []
        
        with self.lock:
            for client_metrics in self.metrics_history.values():
                for metric in client_metrics:
                    if now - metric.timestamp <= seconds:
                        recent_metrics.append(metric)
        
        return sorted(recent_metrics, key=lambda m: m.timestamp)
    
    def get_global_metrics(self) -> Dict:
        """Get aggregated global metrics"""
        now = time.time()
        active_clients = 0
        demo_clients = 0
        real_clients = 0
        total_bandwidth = 0
        
        with self.lock:
            for client_id, metrics in self.metrics_history.items():
                if metrics and now - metrics[-1].timestamp < 5:  # Active in last 5s
                    active_clients += 1
                    total_bandwidth += metrics[-1].bandwidth
                    
                    # Count demo vs real clients
                    is_demo = getattr(metrics[-1], 'is_demo', True)  # Default to demo for backward compatibility
                    if is_demo:
                        demo_clients += 1
                    else:
                        real_clients += 1
            
            return {
                **self.global_metrics,
                'active_connections': active_clients,
                'demo_connections': demo_clients,
                'real_connections': real_clients,
                'total_bandwidth': total_bandwidth,
                'timestamp': now
            }