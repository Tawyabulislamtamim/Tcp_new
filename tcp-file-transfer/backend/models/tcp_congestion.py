import time
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from algorithms.tahoe import TahoeAlgorithm
from algorithms.reno import RenoAlgorithm
from algorithms.cubic import CubicAlgorithm


class CongestionAlgorithm(Enum):
    TAHOE = "tahoe"
    RENO = "reno"
    CUBIC = "cubic"

@dataclass
class NetworkConditions:
    rtt: float = 0.0          # Round-trip time in seconds
    bandwidth: float = 0.0     # Available bandwidth in bytes/second
    packet_loss: float = 0.0   # Packet loss rate (0.0 to 1.0)
    jitter: float = 0.0        # Jitter in seconds

class TCPCongestionControl:
    def __init__(self, initial_algorithm: CongestionAlgorithm = CongestionAlgorithm.RENO):
        self.algorithm_type = initial_algorithm
        self._initialize_algorithm()
        self.network_conditions = NetworkConditions()
        self.last_update_time = time.time()
        self.bytes_in_flight = 0
        self.max_segment_size = 1460  # Typical MSS for Ethernet
        self.retransmit_timeout = 1.0  # Initial RTO in seconds
        self.duplicate_acks = 0
        self.last_ack_number = 0
        self.state = "slow_start"  # slow_start, congestion_avoidance, fast_recovery
        self.congestion_window_history = []
        self.rtt_history = []
        
    def _initialize_algorithm(self):
        """Initialize the selected congestion control algorithm"""
        if self.algorithm_type == CongestionAlgorithm.TAHOE:
            self.algorithm = TahoeAlgorithm()
        elif self.algorithm_type == CongestionAlgorithm.RENO:
            self.algorithm = RenoAlgorithm()
        elif self.algorithm_type == CongestionAlgorithm.CUBIC:
            self.algorithm = CubicAlgorithm()
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm_type}")
    
    def switch_algorithm(self, new_algorithm: CongestionAlgorithm):
        """Switch to a different congestion control algorithm"""
        if new_algorithm != self.algorithm_type:
            self.algorithm_type = new_algorithm
            self._initialize_algorithm()
    
    def on_data_sent(self, bytes_sent: int):
        """Called when new data is sent"""
        self.bytes_in_flight += bytes_sent
        self._update_network_conditions()
    
    def on_ack_received(self, ack_number: int, bytes_acked: int, rtt: Optional[float] = None):
        """
        Called when an ACK is received
        Args:
            ack_number: The sequence number being acknowledged
            bytes_acked: Number of bytes being acknowledged
            rtt: Measured round-trip time (optional)
        """
        current_time = time.time()
        
        # Update RTT measurement if provided
        if rtt is not None:
            self.network_conditions.rtt = rtt
            self.rtt_history.append((current_time, rtt))
            self._update_retransmit_timeout(rtt)
        
        # Detect duplicate ACKs
        if ack_number == self.last_ack_number:
            self.duplicate_acks += 1
        else:
            self.duplicate_acks = 0
            self.last_ack_number = ack_number
        
        # Update algorithm state
        self.algorithm.on_ack_received(ack_number)
        
        # Reduce bytes in flight
        self.bytes_in_flight = max(0, self.bytes_in_flight - bytes_acked)
        
        # Record congestion window
        self.congestion_window_history.append(
            (current_time, self.get_current_cwnd())
        )
        
        self._update_network_conditions()
    
    def on_timeout(self):
        """Called when a packet timeout occurs"""
        self.algorithm.on_timeout()
        self.duplicate_acks = 0
        self._update_network_conditions()
        self._adjust_retransmit_timeout(multiplier=2.0)  # Exponential backoff
    
    def on_loss_detected(self):
        """Called when packet loss is detected (via duplicate ACKs)"""
        if self.algorithm_type == CongestionAlgorithm.CUBIC:
            self.algorithm.on_loss_detected()
        else:
            # For Tahoe and Reno, treat loss same as timeout
            self.on_timeout()
        
        self._update_network_conditions()
    
    def get_current_cwnd(self) -> float:
        """Get the current congestion window size in segments"""
        return self.algorithm.cwnd
    
    def get_ssthresh(self) -> float:
        """Get the current slow start threshold"""
        return self.algorithm.ssthresh
    
    def get_send_window(self) -> int:
        """
        Calculate the current send window size in bytes
        Returns:
            Number of bytes that can be sent now
        """
        window = int(self.algorithm.get_send_window() * self.max_segment_size)
        return max(window, self.max_segment_size)  # Always allow at least one segment
    
    def get_current_algorithm(self) -> str:
        """Get the name of the current algorithm"""
        return self.algorithm_type.value
    
    def get_network_congestion_factor(self) -> float:
        """
        Calculate a heuristic congestion factor (0.0 to 1.0)
        Higher values indicate more congestion
        """
        loss_factor = self.network_conditions.packet_loss * 10  # Weight packet loss more heavily
        rtt_factor = min(self.network_conditions.rtt / 0.5, 1.0)  # Normalize RTT to 500ms
        return min(loss_factor + rtt_factor, 1.0)
    
    def get_packet_loss_rate(self) -> float:
        """Get the current estimated packet loss rate"""
        return self.network_conditions.packet_loss
    
    def _update_network_conditions(self):
        """Update network condition estimates"""
        current_time = time.time()
        time_elapsed = current_time - self.last_update_time
        
        # Simple heuristic for packet loss based on duplicate ACKs
        if self.duplicate_acks >= 3:
            self.network_conditions.packet_loss = min(
                0.5, self.network_conditions.packet_loss + 0.1
            )
        else:
            # Gradually reduce packet loss estimate when no congestion
            self.network_conditions.packet_loss = max(
                0.0, self.network_conditions.packet_loss - 0.01
            )
        
        # Bandwidth estimate based on recent throughput
        if time_elapsed > 0 and self.bytes_in_flight > 0:
            self.network_conditions.bandwidth = self.bytes_in_flight / time_elapsed
        
        self.last_update_time = current_time
    
    def _update_retransmit_timeout(self, rtt: float):
        """
        Update retransmit timeout using Jacobson/Karels algorithm
        Args:
            rtt: Measured round-trip time
        """
        if not hasattr(self, 'srtt'):
            # First measurement
            self.srtt = rtt
            self.rttvar = rtt / 2
        else:
            # Update estimates
            self.rttvar = 0.75 * self.rttvar + 0.25 * abs(self.srtt - rtt)
            self.srtt = 0.875 * self.srtt + 0.125 * rtt
        
        # Calculate RTO with bounds
        self.retransmit_timeout = self.srtt + max(0.1, 4 * self.rttvar)
        self.retransmit_timeout = min(max(self.retransmit_timeout, 0.1), 60.0)  # Clamp between 100ms and 60s
    
    def _adjust_retransmit_timeout(self, multiplier: float = 2.0):
        """Exponentially increase the retransmit timeout"""
        self.retransmit_timeout = min(
            self.retransmit_timeout * multiplier,
            60.0  # Maximum 60 seconds
        )
    
    def get_metrics(self) -> dict:
        """Get current congestion control metrics"""
        return {
            "algorithm": self.get_current_algorithm(),
            "cwnd": self.get_current_cwnd(),
            "ssthresh": self.get_ssthresh(),
            "send_window": self.get_send_window(),
            "rtt": self.network_conditions.rtt,
            "bandwidth": self.network_conditions.bandwidth,
            "packet_loss": self.network_conditions.packet_loss,
            "state": self.state,
            "duplicate_acks": self.duplicate_acks,
            "retransmit_timeout": self.retransmit_timeout
        }