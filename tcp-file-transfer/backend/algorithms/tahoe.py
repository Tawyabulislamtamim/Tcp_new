class TahoeAlgorithm:
    def __init__(self):
        self.cwnd = 1.0  # Congestion window
        self.ssthresh = 65535  # Slow start threshold
        self.state = 'slow_start'  # slow_start, congestion_avoidance
        self.duplicate_acks = 0
        self.last_ack = 0
        
    def on_ack_received(self, ack_num):
        if self.state == 'slow_start':
            self.cwnd += 1
            if self.cwnd >= self.ssthresh:
                self.state = 'congestion_avoidance'
        elif self.state == 'congestion_avoidance':
            self.cwnd += 1.0 / self.cwnd
            
    def on_timeout(self):
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = 1.0
        self.state = 'slow_start'
        
    def get_send_window(self):
        return int(self.cwnd)