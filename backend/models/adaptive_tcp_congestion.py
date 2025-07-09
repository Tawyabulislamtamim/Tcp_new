import time
import random
from enum import Enum
from algorithms import RenoAlgorithm, CubicAlgorithm, TahoeAlgorithm
from algorithms.bbr import BBRAlgorithm

class AlgorithmType(Enum):
    RENO = "reno"
    CUBIC = "cubic"
    TAHOE = "tahoe"
    BBR = "bbr"

class NetworkCondition(Enum):
    EXCELLENT = "excellent"  # Low latency, low loss
    GOOD = "good"           # Normal conditions
    CONGESTED = "congested" # High latency, some loss
    LOSSY = "lossy"        # High packet loss
    HIGH_BW = "high_bw"    # High bandwidth, long delay

class AdaptiveTCPCongestionControl:
    """
    Enhanced TCP Congestion Control with Dynamic Algorithm Switching
    Automatically adapts to network conditions by switching between algorithms
    """
    
    def __init__(self, initial_algorithm: AlgorithmType = AlgorithmType.RENO):
        self.algorithm_type = initial_algorithm
        self._initialize_algorithm()
        
        # Network condition tracking
        self.packets_sent = 0
        self.packets_lost = 0
        self.rtt_history = []
        self.bandwidth_history = []
        self.start_time = time.time()
        self.last_switch_time = time.time()
        self.switch_cooldown = 10.0  # Minimum 10 seconds between switches
        
        # Thresholds for network condition detection
        self.rtt_threshold_high = 100.0  # ms
        self.rtt_threshold_excellent = 20.0  # ms
        self.loss_threshold_high = 0.02  # 2%
        self.loss_threshold_low = 0.001  # 0.1%
        self.bandwidth_threshold_high = 10 * 1024 * 1024  # 10 MB/s
        
        # Algorithm performance tracking
        self.algorithm_performance = {
            AlgorithmType.RENO: {"switches": 0, "total_time": 0, "performance_score": 0},
            AlgorithmType.CUBIC: {"switches": 0, "total_time": 0, "performance_score": 0},
            AlgorithmType.TAHOE: {"switches": 0, "total_time": 0, "performance_score": 0},
            AlgorithmType.BBR: {"switches": 0, "total_time": 0, "performance_score": 0}
        }
        
    def _initialize_algorithm(self):
        """Initialize the selected algorithm"""
        if self.algorithm_type == AlgorithmType.RENO:
            self.algorithm = RenoAlgorithm()
        elif self.algorithm_type == AlgorithmType.CUBIC:
            self.algorithm = CubicAlgorithm()
        elif self.algorithm_type == AlgorithmType.TAHOE:
            self.algorithm = TahoeAlgorithm()
        elif self.algorithm_type == AlgorithmType.BBR:
            self.algorithm = BBRAlgorithm()
    
    def detect_network_condition(self) -> NetworkCondition:
        """Detect current network conditions based on metrics"""
        if len(self.rtt_history) < 5:
            return NetworkCondition.GOOD
        
        # Calculate recent averages
        recent_rtt = sum(self.rtt_history[-10:]) / min(len(self.rtt_history), 10)
        loss_rate = self.get_packet_loss_rate()
        recent_bandwidth = sum(self.bandwidth_history[-5:]) / min(len(self.bandwidth_history), 5) if self.bandwidth_history else 0
        
        # Classify network condition
        if loss_rate > self.loss_threshold_high:
            return NetworkCondition.LOSSY
        elif recent_rtt > self.rtt_threshold_high:
            if recent_bandwidth > self.bandwidth_threshold_high:
                return NetworkCondition.HIGH_BW  # High bandwidth, high delay (long fat network)
            else:
                return NetworkCondition.CONGESTED
        elif recent_rtt < self.rtt_threshold_excellent and loss_rate < self.loss_threshold_low:
            return NetworkCondition.EXCELLENT
        else:
            return NetworkCondition.GOOD
    
    def get_optimal_algorithm(self, condition: NetworkCondition) -> AlgorithmType:
        """Determine optimal algorithm for given network condition"""
        algorithm_mapping = {
            NetworkCondition.EXCELLENT: AlgorithmType.BBR,      # BBR excels in clean networks
            NetworkCondition.GOOD: AlgorithmType.CUBIC,        # CUBIC for general use
            NetworkCondition.CONGESTED: AlgorithmType.RENO,    # Reno's conservative approach
            NetworkCondition.LOSSY: AlgorithmType.TAHOE,       # Tahoe's simple, robust approach
            NetworkCondition.HIGH_BW: AlgorithmType.CUBIC      # CUBIC designed for high-BW
        }
        return algorithm_mapping.get(condition, AlgorithmType.RENO)
    
    def should_switch_algorithm(self, target_algorithm: AlgorithmType) -> bool:
        """Determine if algorithm switch is beneficial"""
        current_time = time.time()
        
        # Respect cooldown period
        if current_time - self.last_switch_time < self.switch_cooldown:
            return False
        
        # Don't switch to same algorithm
        if target_algorithm == self.algorithm_type:
            return False
        
        # Check if target algorithm has better historical performance
        current_perf = self.algorithm_performance[self.algorithm_type]["performance_score"]
        target_perf = self.algorithm_performance[target_algorithm]["performance_score"]
        
        # Switch if target is significantly better or current is underperforming
        if target_perf > current_perf * 1.1 or current_perf < 0.5:
            return True
        
        return True  # Default to switch for adaptation
    
    def calculate_performance_score(self) -> float:
        """Calculate performance score for current algorithm"""
        if self.packets_sent == 0:
            return 0.5
        
        # Factors: throughput (positive), loss rate (negative), stability (positive)
        loss_rate = self.get_packet_loss_rate()
        avg_bandwidth = sum(self.bandwidth_history[-10:]) / min(len(self.bandwidth_history), 10) if self.bandwidth_history else 0
        rtt_stability = 1.0 / (1.0 + self._calculate_rtt_variance())
        
        # Normalized score (0-1)
        throughput_score = min(avg_bandwidth / 1000000, 1.0)  # Normalize to 1MB/s
        loss_penalty = 1.0 - min(loss_rate * 50, 1.0)  # Heavy penalty for loss
        stability_score = rtt_stability
        
        return (throughput_score * 0.5 + loss_penalty * 0.3 + stability_score * 0.2)
    
    def _calculate_rtt_variance(self) -> float:
        """Calculate RTT variance for stability assessment"""
        if len(self.rtt_history) < 3:
            return 0.0
        
        recent_rtts = self.rtt_history[-10:]
        mean_rtt = sum(recent_rtts) / len(recent_rtts)
        variance = sum((rtt - mean_rtt) ** 2 for rtt in recent_rtts) / len(recent_rtts)
        return variance ** 0.5  # Standard deviation
    
    def adaptive_algorithm_switch(self, rtt: float, bandwidth: float):
        """Main function to handle adaptive algorithm switching"""
        # Update history
        self.rtt_history.append(rtt)
        self.bandwidth_history.append(bandwidth)
        
        # Keep history bounded
        if len(self.rtt_history) > 50:
            self.rtt_history = self.rtt_history[-50:]
        if len(self.bandwidth_history) > 50:
            self.bandwidth_history = self.bandwidth_history[-50:]
        
        # Update current algorithm performance
        current_score = self.calculate_performance_score()
        self.algorithm_performance[self.algorithm_type]["performance_score"] = current_score
        
        # Detect network condition
        condition = self.detect_network_condition()
        optimal_algorithm = self.get_optimal_algorithm(condition)
        
        # Decide whether to switch
        if self.should_switch_algorithm(optimal_algorithm):
            self.switch_algorithm(optimal_algorithm, f"Network condition: {condition.value}")
    
    def switch_algorithm(self, new_algorithm: AlgorithmType, reason: str = "Manual"):
        """Dynamically switch congestion control algorithm"""
        if new_algorithm == self.algorithm_type:
            return
        
        old_algorithm = self.algorithm_type
        
        # Save current state
        current_cwnd = getattr(self.algorithm, 'cwnd', 1.0)
        current_ssthresh = getattr(self.algorithm, 'ssthresh', 65535)
        
        # Update performance tracking
        current_time = time.time()
        self.algorithm_performance[old_algorithm]["total_time"] += current_time - self.last_switch_time
        self.algorithm_performance[new_algorithm]["switches"] += 1
        
        # Switch algorithm
        self.algorithm_type = new_algorithm
        self._initialize_algorithm()
        
        # Maintain state continuity where possible
        if hasattr(self.algorithm, 'cwnd'):
            self.algorithm.cwnd = current_cwnd
        if hasattr(self.algorithm, 'ssthresh'):
            self.algorithm.ssthresh = current_ssthresh
        
        self.last_switch_time = current_time
        
        print(f"Algorithm switched: {old_algorithm.value} -> {new_algorithm.value} ({reason})")
    
    def on_ack_received(self, ack_num: int, rtt: float = None, bandwidth: float = None):
        """Handle incoming ACK with adaptive switching"""
        # Standard ACK processing
        if hasattr(self.algorithm, 'on_ack_received'):
            if self.algorithm_type == AlgorithmType.BBR and rtt and bandwidth:
                # BBR needs additional parameters
                self.algorithm.on_ack_received(ack_num, rtt=rtt, delivered_bytes=1024, elapsed_time=0.001)
            else:
                self.algorithm.on_ack_received(ack_num)
        
        # Adaptive switching logic
        if rtt and bandwidth:
            self.adaptive_algorithm_switch(rtt, bandwidth)
    
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
        if hasattr(self.algorithm, 'cwnd'):
            return self.algorithm.cwnd
        elif hasattr(self.algorithm, 'get_current_cwnd'):
            return self.algorithm.get_current_cwnd()
        return 1.0
    
    def get_ssthresh(self) -> float:
        """Get current slow start threshold"""
        return getattr(self.algorithm, 'ssthresh', 65535)
    
    def get_packet_loss_rate(self) -> float:
        """Calculate packet loss rate"""
        if self.packets_sent == 0:
            return 0.0
        return self.packets_lost / self.packets_sent
    
    def get_current_algorithm(self) -> str:
        """Get current algorithm name"""
        return self.algorithm_type.value
    
    def get_algorithm_state(self) -> str:
        """Get detailed algorithm state"""
        if hasattr(self.algorithm, 'state'):
            return self.algorithm.state
        elif hasattr(self.algorithm, 'get_state'):
            return self.algorithm.get_state()
        return "unknown"
    
    def get_network_condition(self) -> str:
        """Get current detected network condition"""
        return self.detect_network_condition().value
    
    def get_performance_metrics(self) -> dict:
        """Get comprehensive performance metrics"""
        return {
            "current_algorithm": self.get_current_algorithm(),
            "algorithm_state": self.get_algorithm_state(),
            "network_condition": self.get_network_condition(),
            "cwnd": self.get_current_cwnd(),
            "ssthresh": self.get_ssthresh(),
            "loss_rate": self.get_packet_loss_rate(),
            "packets_sent": self.packets_sent,
            "packets_lost": self.packets_lost,
            "algorithm_performance": self.algorithm_performance,
            "switch_history": {
                "last_switch": self.last_switch_time,
                "time_since_switch": time.time() - self.last_switch_time
            }
        }

# Legacy compatibility class
class TCPCongestionControl(AdaptiveTCPCongestionControl):
    """Legacy compatibility wrapper"""
    def __init__(self, algorithm='reno'):
        algorithm_map = {
            'reno': AlgorithmType.RENO,
            'cubic': AlgorithmType.CUBIC,
            'tahoe': AlgorithmType.TAHOE,
            'bbr': AlgorithmType.BBR
        }
        super().__init__(algorithm_map.get(algorithm, AlgorithmType.RENO))
