import time
import threading
from typing import Generator, Optional
from pathlib import Path
from .connection_manager import ConnectionManager
from .metrics_collector import NetworkMetrics

class TransferHandler:
    def __init__(self, connection_manager: ConnectionManager, chunk_size: int = 8192):
        self.connection_manager = connection_manager
        self.chunk_size = chunk_size
        self.active_transfers = {}
        self.lock = threading.Lock()
        
    def start_transfer(self, client_id: str, file_path: Path, file_size: int) -> str:
        transfer_id = f"{client_id}_{int(time.time())}"
        
        with self.lock:
            self.active_transfers[transfer_id] = {
                'client_id': client_id,
                'file_path': file_path,
                'file_size': file_size,
                'bytes_sent': 0,
                'start_time': time.time(),
                'last_chunk_time': time.time()
            }
            
        return transfer_id
        
    def generate_file_chunks(self, transfer_id: str) -> Generator[bytes, None, None]:
        if transfer_id not in self.active_transfers:
            return
            
        transfer_info = self.active_transfers[transfer_id]
        client = self.connection_manager.get_client(transfer_info['client_id'])
        
        if not client:
            return
            
        try:
            with open(transfer_info['file_path'], 'rb') as file:
                while True:
                    # Get current congestion window
                    cwnd = client.tcp_controller.get_current_cwnd()
                    
                    # Calculate dynamic chunk size based on cwnd
                    dynamic_chunk_size = min(self.chunk_size * int(cwnd), 65536)
                    
                    chunk = file.read(dynamic_chunk_size)
                    if not chunk:
                        break
                        
                    # Update transfer statistics
                    current_time = time.time()
                    transfer_info['bytes_sent'] += len(chunk)
                    
                    # Calculate metrics
                    time_diff = current_time - transfer_info['last_chunk_time']
                    if time_diff > 0:
                        bandwidth = len(chunk) / time_diff
                        
                        # Simulate RTT measurement (in real implementation, measure actual RTT)
                        rtt = self._measure_rtt(client)
                        
                        # Record metrics
                        metrics = NetworkMetrics(
                            timestamp=current_time,
                            cwnd=cwnd,
                            ssthresh=client.tcp_controller.get_ssthresh(),
                            rtt=rtt,
                            bandwidth=bandwidth,
                            packet_loss=client.tcp_controller.get_packet_loss_rate(),
                            algorithm=client.tcp_controller.get_current_algorithm(),
                            client_id=transfer_info['client_id']
                        )
                        
                        self.connection_manager.metrics_collector.record_metrics(
                            transfer_info['client_id'], metrics
                        )
                        
                        # Update TCP controller
                        client.tcp_controller.on_data_sent(len(chunk))
                    
                    transfer_info['last_chunk_time'] = current_time
                    
                    yield chunk
                    
                    # Apply congestion control delay if needed
                    if cwnd < 4:  # Slow start or heavy congestion
                        time.sleep(0.001)  # Small delay
                        
        except Exception as e:
            print(f"Transfer error: {e}")
        finally:
            with self.lock:
                if transfer_id in self.active_transfers:
                    del self.active_transfers[transfer_id]
                    
    def _measure_rtt(self, client) -> float:
        # Simplified RTT measurement
        # In a real implementation, you'd measure actual round-trip time
        return 0.05 + (0.02 * client.tcp_controller.get_network_congestion_factor())
        
    def get_transfer_progress(self, transfer_id: str) -> Optional[dict]:
        with self.lock:
            if transfer_id not in self.active_transfers:
                return None
                
            transfer = self.active_transfers[transfer_id]
            elapsed_time = time.time() - transfer['start_time']
            
            return {
                'transfer_id': transfer_id,
                'file_size': transfer['file_size'],
                'bytes_sent': transfer['bytes_sent'],
                'progress': transfer['bytes_sent'] / transfer['file_size'] if transfer['file_size'] > 0 else 0,
                'elapsed_time': elapsed_time,
                'average_speed': transfer['bytes_sent'] / elapsed_time if elapsed_time > 0 else 0
            }