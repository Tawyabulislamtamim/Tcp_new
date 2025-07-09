import time
from enum import Enum
from algorithms import RenoAlgorithm, CubicAlgorithm, TahoeAlgorithm, BBRAlgorithm

class AlgorithmType(Enum):
    RENO = "reno"
    CUBIC = "cubic"
    TAHOE = "tahoe"
    BBR = "bbr"

class TCPCongestionControl:
    def __init__(self, initial_algorithm: AlgorithmType = AlgorithmType.RENO):
        self.algorithm_type = initial_algorithm
        self._initialize_algorithm()
        self.packets_sent = 0
        self.packets_lost = 0
        self.start_time = time.time()
        
    def _initialize_algorithm(self):
        if self.algorithm_type == AlgorithmType.RENO:
            self.algorithm = RenoAlgorithm()
        elif self.algorithm_type == AlgorithmType.CUBIC:
            self.algorithm = CubicAlgorithm()
        elif self.algorithm_type == AlgorithmType.TAHOE:
            self.algorithm = TahoeAlgorithm()
        elif self.algorithm_type == AlgorithmType.BBR:
            self.algorithm = BBRAlgorithm()
    
    def switch_algorithm(self, new_algorithm: AlgorithmType):
        """Dynamically switch congestion control algorithm"""
        # Save current state
        current_cwnd = self.algorithm.cwnd
        current_ssthresh = self.algorithm.ssthresh
        
        # Switch algorithm
        self.algorithm_type = new_algorithm
        self._initialize_algorithm()
        
        # Maintain continuity
        self.algorithm.cwnd = current_cwnd
        self.algorithm.ssthresh = current_ssthresh
    
    def on_ack_received(self, ack_num: int):
        """Handle incoming ACK"""
        self.algorithm.on_ack_received(ack_num)
    
    def on_loss_detected(self):
        """Handle packet loss detection"""
        self.packets_lost += 1
        if hasattr(self.algorithm, 'on_loss_detected'):
            self.algorithm.on_loss_detected()
        elif hasattr(self.algorithm, 'on_timeout'):
            self.algorithm.on_timeout()
    
    def on_data_sent(self, bytes_sent: int):
        """Record data transmission"""
        self.packets_sent += 1
    
    def get_current_cwnd(self) -> float:
        """Get current congestion window size"""
        return self.algorithm.cwnd
    
    def get_ssthresh(self) -> float:
        """Get current slow start threshold"""
        return self.algorithm.ssthresh
    
    def get_packet_loss_rate(self) -> float:
        """Calculate packet loss rate"""
        if self.packets_sent == 0:
            return 0.0
        return self.packets_lost / self.packets_sent
    
    def get_current_algorithm(self) -> str:
        """Get current algorithm name"""
        return self.algorithm_type.value
    
    def get_network_congestion_factor(self) -> float:
        """Calculate a synthetic congestion factor (0-1)"""
        loss_rate = self.get_packet_loss_rate()
        cwnd_ratio = self.algorithm.cwnd / self.algorithm.ssthresh
        return min(loss_rate * 2 + (1 - cwnd_ratio), 1.0)
    
    def evaluate_and_switch_algorithm(self, current_rtt: float, bandwidth: float, loss_rate: float):
        """
        Dynamically switch algorithms based on network conditions
        
        Args:
            current_rtt: Current round-trip time in milliseconds
            bandwidth: Current bandwidth in bytes/second
            loss_rate: Current packet loss rate (0.0 to 1.0)
        """
        # Get current network conditions
        high_bandwidth = bandwidth > 1_000_000  # > 1 MB/s
        high_latency = current_rtt > 100  # > 100ms
        high_loss = loss_rate > 0.01  # > 1% loss
        low_loss = loss_rate < 0.001  # < 0.1% loss
        
        # Current algorithm
        current_algo = self.algorithm_type
        new_algo = current_algo
        
        # Decision logic based on network conditions
        if high_bandwidth and high_latency and low_loss:
            # High BDP network with low loss - BBR is optimal
            new_algo = AlgorithmType.BBR
            
        elif high_bandwidth and not high_latency and low_loss:
            # High bandwidth, low latency - CUBIC works well
            new_algo = AlgorithmType.CUBIC
            
        elif high_loss and not high_bandwidth:
            # High loss, moderate bandwidth - Reno's conservative approach
            new_algo = AlgorithmType.RENO
            
        elif high_loss and high_latency:
            # High loss, high latency - Tahoe's simple approach
            new_algo = AlgorithmType.TAHOE
            
        elif high_bandwidth and not high_loss:
            # High bandwidth, moderate conditions - CUBIC
            new_algo = AlgorithmType.CUBIC
            
        # Only switch if algorithm would actually change
        if new_algo != current_algo:
            print(f"Switching from {current_algo.value} to {new_algo.value} "
                  f"(RTT: {current_rtt:.1f}ms, BW: {bandwidth/1024:.1f}KB/s, Loss: {loss_rate*100:.2f}%)")
            self.switch_algorithm(new_algo)
            return True
        
        return False
    
    def get_algorithm_recommendations(self) -> dict:
        """Get information about when each algorithm is recommended"""
        return {
            "BBR": "High bandwidth-delay product networks with low loss",
            "CUBIC": "High bandwidth networks with moderate latency",
            "RENO": "Networks with moderate loss rates",
            "TAHOE": "High loss or unstable networks"
        }