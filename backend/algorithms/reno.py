class RenoAlgorithm:
    def __init__(self):
        self.cwnd = 1.0
        self.ssthresh = 65535
        self.state = 'slow_start'  # slow_start, congestion_avoidance, fast_recovery
        self.duplicate_acks = 0
        self.recover = 0
        
    def on_ack_received(self, ack_num):
        if self.state == 'fast_recovery':
            if ack_num > self.recover:
                self.cwnd = self.ssthresh
                self.state = 'congestion_avoidance'
                self.duplicate_acks = 0
            else:
                self.cwnd += 1
        elif self.duplicate_acks >= 3:
            self.enter_fast_recovery(ack_num)
        else:
            # Normal ACK processing
            if self.state == 'slow_start':
                self.cwnd += 1
                if self.cwnd >= self.ssthresh:
                    self.state = 'congestion_avoidance'
            elif self.state == 'congestion_avoidance':
                self.cwnd += 1.0 / self.cwnd
                
    def enter_fast_recovery(self, ack_num):
        self.ssthresh = max(self.cwnd / 2, 2)
        self.cwnd = self.ssthresh + 3
        self.state = 'fast_recovery'
        self.recover = ack_num