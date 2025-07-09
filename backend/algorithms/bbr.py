import time
import math

class BBRAlgorithm:
    """
    BBR (Bottleneck Bandwidth and Round-trip time) Congestion Control Algorithm
    Based on Google's BBR algorithm for optimizing both throughput and latency
    """
    
    def __init__(self):
        # Core BBR state variables
        self.bw_estimate = 1000000  # Bandwidth estimate in bytes/sec (start with 1MB/s)
        self.min_rtt = float('inf')  # Minimum RTT observed
        self.rtprop_stamp = 0  # Time when min_rtt was last updated
        self.probe_rtt_done_stamp = 0
        
        # Pacing and sending control
        self.pacing_rate = self.bw_estimate  # Bytes per second
        self.cwnd = 10.0  # Initial congestion window
        self.ssthresh = 65535
        
        # BBR state machine
        self.state = 'STARTUP'  # STARTUP, DRAIN, PROBE_BW, PROBE_RTT
        self.cycle_index = 0  # For PROBE_BW cycling
        self.cycle_stamp = 0  # When current cycle started
        self.prior_cwnd = 0
        
        # Configuration constants
        self.bbr_high_gain = 2.885  # Startup/DRAIN gain
        self.bbr_drain_gain = 1.0 / 2.885
        self.bbr_cwnd_gain = 2.0  # Congestion window gain
        self.bbr_probe_rtt_time = 0.2  # 200ms probe RTT duration
        self.bbr_rtprop_filterlen = 10.0  # 10 seconds
        
        # PROBE_BW cycle gains
        self.pacing_gain_cycle = [1.25, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        self.pacing_gain = 1.0
        
        # Tracking variables
        self.packet_count = 0
        self.delivered = 0  # Total bytes delivered
        self.delivery_rate = 0  # Current delivery rate
        self.round_start = True
        self.full_bw_reached = False
        self.full_bw = 0
        self.full_bw_count = 0
        
    def update_bandwidth_estimate(self, delivered_bytes, elapsed_time):
        """Update bandwidth estimate based on delivered bytes and time"""
        if elapsed_time > 0:
            current_bw = delivered_bytes / elapsed_time
            # Use maximum of recent bandwidth estimates
            if current_bw > self.bw_estimate or elapsed_time > 1.0:
                self.bw_estimate = current_bw
    
    def update_min_rtt(self, rtt):
        """Update minimum RTT estimate"""
        current_time = time.time()
        
        # Update min_rtt if we see a new minimum or it's been too long
        if rtt < self.min_rtt or (current_time - self.rtprop_stamp) > self.bbr_rtprop_filterlen:
            self.min_rtt = rtt
            self.rtprop_stamp = current_time
    
    def check_startup_done(self):
        """Check if startup phase is complete"""
        if self.full_bw_reached:
            return True
            
        # Check if bandwidth growth has plateaued
        if self.bw_estimate >= self.full_bw * 1.25:
            self.full_bw = self.bw_estimate
            self.full_bw_count = 0
        else:
            self.full_bw_count += 1
            
        if self.full_bw_count >= 3:
            self.full_bw_reached = True
            return True
            
        return False
    
    def set_pacing_rate(self):
        """Set pacing rate based on current bandwidth estimate and gain"""
        rate = self.bw_estimate * self.pacing_gain
        self.pacing_rate = max(rate, 1000)  # Minimum 1KB/s
    
    def set_cwnd(self):
        """Set congestion window based on BDP and gain"""
        if self.min_rtt == float('inf'):
            return
            
        # Calculate Bandwidth-Delay Product
        bdp = self.bw_estimate * self.min_rtt
        cwnd = bdp * self.bbr_cwnd_gain
        
        # Minimum window of 4 packets
        self.cwnd = max(cwnd, 4.0)
        
        # In PROBE_RTT, use smaller window
        if self.state == 'PROBE_RTT':
            self.cwnd = max(4.0, bdp)
    
    def advance_cycle_phase(self):
        """Advance to next phase in PROBE_BW cycle"""
        current_time = time.time()
        if current_time - self.cycle_stamp > self.min_rtt:
            self.cycle_index = (self.cycle_index + 1) % len(self.pacing_gain_cycle)
            self.pacing_gain = self.pacing_gain_cycle[self.cycle_index]
            self.cycle_stamp = current_time
    
    def check_probe_rtt(self):
        """Check if we should enter PROBE_RTT state"""
        current_time = time.time()
        if self.state != 'PROBE_RTT' and \
           (current_time - self.rtprop_stamp) > self.bbr_rtprop_filterlen:
            self.state = 'PROBE_RTT'
            self.pacing_gain = 1.0
            self.prior_cwnd = self.cwnd
            self.probe_rtt_done_stamp = current_time + self.bbr_probe_rtt_time
    
    def handle_probe_rtt(self):
        """Handle PROBE_RTT state logic"""
        current_time = time.time()
        if current_time >= self.probe_rtt_done_stamp:
            self.rtprop_stamp = current_time
            if self.prior_cwnd > 0:
                self.cwnd = max(self.cwnd, self.prior_cwnd)
            # Return to PROBE_BW
            self.state = 'PROBE_BW'
            self.cycle_index = 0
            self.pacing_gain = self.pacing_gain_cycle[0]
            self.cycle_stamp = current_time
    
    def on_ack_received(self, ack_num, rtt=None, delivered_bytes=0, elapsed_time=0):
        """Handle incoming ACK with BBR logic"""
        current_time = time.time()
        
        # Update estimates
        if rtt:
            self.update_min_rtt(rtt)
        
        if elapsed_time > 0:
            self.update_bandwidth_estimate(delivered_bytes, elapsed_time)
        
        # State machine
        if self.state == 'STARTUP':
            self.pacing_gain = self.bbr_high_gain
            if self.check_startup_done():
                self.state = 'DRAIN'
                self.pacing_gain = self.bbr_drain_gain
                
        elif self.state == 'DRAIN':
            if self.cwnd <= self.bw_estimate * self.min_rtt:
                self.state = 'PROBE_BW'
                self.cycle_index = 0
                self.pacing_gain = 1.0
                self.cycle_stamp = current_time
                
        elif self.state == 'PROBE_BW':
            self.advance_cycle_phase()
            
        # Check for PROBE_RTT
        self.check_probe_rtt()
        
        if self.state == 'PROBE_RTT':
            self.handle_probe_rtt()
        
        # Update pacing rate and cwnd
        self.set_pacing_rate()
        self.set_cwnd()
        
        self.packet_count += 1
    
    def on_loss_detected(self):
        """Handle packet loss - BBR doesn't react strongly to single losses"""
        # BBR doesn't reduce cwnd on single packet loss like traditional algorithms
        # It relies on bandwidth and RTT measurements instead
        pass
    
    def get_current_cwnd(self):
        """Get current congestion window"""
        return self.cwnd
    
    def get_pacing_rate(self):
        """Get current pacing rate"""
        return self.pacing_rate
    
    def get_state(self):
        """Get current BBR state"""
        return self.state
    
    def get_bandwidth_estimate(self):
        """Get current bandwidth estimate"""
        return self.bw_estimate
