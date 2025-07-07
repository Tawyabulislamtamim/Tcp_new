import math
import time

class CubicAlgorithm:
    def __init__(self):
        self.cwnd = 1.0
        self.ssthresh = 65535
        self.state = 'slow_start'
        self.wmax = 0
        self.epoch_start = 0
        self.origin_point = 0
        self.c = 0.4  # Cubic scaling factor
        self.beta = 0.7  # Multiplicative decrease factor
        
    def cubic_function(self, t):
        return self.c * ((t - self.origin_point) ** 3) + self.wmax
        
    def on_ack_received(self, ack_num):
        if self.state == 'slow_start':
            self.cwnd += 1
            if self.cwnd >= self.ssthresh:
                self.state = 'congestion_avoidance'
                self.epoch_start = time.time()
        elif self.state == 'congestion_avoidance':
            t = time.time() - self.epoch_start
            target_cwnd = self.cubic_function(t)
            
            if target_cwnd > self.cwnd:
                self.cwnd = min(target_cwnd, self.cwnd + 1.0/self.cwnd)
            else:
                self.cwnd += 1.0 / self.cwnd
                
    def on_loss_detected(self):
        self.wmax = self.cwnd
        self.cwnd = self.cwnd * self.beta
        self.ssthresh = self.cwnd
        self.state = 'congestion_avoidance'
        self.epoch_start = time.time()
        self.origin_point = (self.wmax * (1 - self.beta) / self.c) ** (1/3)