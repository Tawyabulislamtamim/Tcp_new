from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional

class CongestionAlgorithm(Enum):
    TAHOE = auto()
    RENO = auto()
    CUBIC = auto()

@dataclass
class FileTransferRequest:
    file_path: str
    client_id: str
    algorithm: CongestionAlgorithm = CongestionAlgorithm.RENO
    chunk_size: int = 8192

@dataclass
class FileTransferResponse:
    transfer_id: str
    file_size: int
    status: str
    message: Optional[str] = None

@dataclass
class NetworkMetrics:
    timestamp: float
    cwnd: float
    ssthresh: float
    rtt: float
    bandwidth: float
    packet_loss: float
    algorithm: str