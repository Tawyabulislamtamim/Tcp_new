# TCP File Transfer System - Metrics Setup

A comprehensive TCP file transfer system with real-time metrics dashboard demonstrating various TCP congestion control algorithms (Reno, Tahoe, CUBIC).

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ with virtual environment
- Node.js 14+ and npm
- Modern web browser

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\Activate
pip install -r requirements.txt
python app.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Docker Setup (Alternative)
```bash
docker-compose up
```

## 📊 Metrics System

### What's Included

#### Real-time Metrics Dashboard
- **Live Network Statistics**: Active connections, bandwidth, RTT, data transferred
- **Congestion Control Graphs**: Real-time visualization of cwnd, ssthresh, bandwidth, and RTT
- **Algorithm Comparison**: Side-by-side comparison of Reno, Tahoe, and CUBIC algorithms
- **Time Range Selection**: View metrics for last 30s, 1m, 2m, or 5m

#### TCP Congestion Control Algorithms
1. **TCP Reno**: Classic algorithm with fast recovery
2. **TCP Tahoe**: Simpler algorithm without fast recovery  
3. **TCP CUBIC**: Modern algorithm optimized for high-bandwidth networks

#### API Endpoints
- `GET /api/metrics/global` - Global network metrics
- `GET /api/metrics/history?seconds=X` - Historical metrics data
- `GET /api/metrics/stream` - Server-sent events for real-time updates
- `GET /api/metrics/client/{id}` - Client-specific metrics

### Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Metrics       │
│   (React)       │◄──►│   (Flask)       │◄──►│   Collector     │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Dashboard   │ │    │ │ API Routes  │ │    │ │ TCP Algo    │ │
│ │ Components  │ │    │ │             │ │    │ │ Simulation  │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Graphs      │ │    │ │ WebSocket   │ │    │ │ Metrics     │ │
│ │ (Recharts)  │ │    │ │ / SSE       │ │    │ │ Storage     │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

#### Backend (`backend/`)
- **`models/metrics_collector.py`**: Collects and stores network metrics
- **`models/tcp_congestion.py`**: Implements TCP congestion control algorithms
- **`api/metrics.py`**: REST API endpoints for metrics data
- **`app.py`**: Main Flask application with background metrics generation

#### Frontend (`frontend/src/`)
- **`components/MetricsDashboard/`**: Complete metrics dashboard
- **`services/metricsService.js`**: API client for metrics data
- **`hooks/useMetrics.js`**: React hook for metrics state management

## 🎯 Features

### Real-time Updates
- Server-sent events (SSE) for live metrics streaming
- Automatic refresh every 2 seconds
- Connection status indicators

### Interactive Graphs
- **Congestion Window & Slow Start Threshold**: Track algorithm behavior
- **Bandwidth & RTT**: Monitor network performance
- **Time Range Selection**: Analyze different time periods
- **Algorithm Tags**: Visual indicators of active algorithms

### Network Statistics Cards
- Active connections count
- Total bandwidth utilization  
- Average round-trip time
- Total data transferred

### Error Handling
- Connection error detection
- Graceful fallback for disconnected state
- Retry mechanisms for failed requests

## 🔧 Configuration

### Backend Configuration (`backend/config.py`)
```python
# Metrics collection settings
CLEANUP_INTERVAL = 60  # seconds
CLIENT_TIMEOUT = 300   # seconds
DEFAULT_ALGORITHM = 'reno'
CHUNK_SIZE = 8192
```

### Frontend Configuration
```javascript
// API base URL
REACT_APP_API_URL=http://localhost:5000/api

// Metrics refresh interval
const METRICS_REFRESH_INTERVAL = 2000; // ms
```

## 📈 Understanding the Metrics

### Congestion Window (cwnd)
- Represents the number of packets that can be sent without acknowledgment
- Increases during slow start and congestion avoidance phases
- Decreases when packet loss is detected

### Slow Start Threshold (ssthresh)
- Threshold value that determines when to switch from slow start to congestion avoidance
- Set to half of cwnd when congestion is detected

### Round Trip Time (RTT)
- Time for a packet to travel from sender to receiver and back
- Used to calculate timeouts and detect packet loss

### Bandwidth
- Current data transmission rate in bytes/second
- Affected by network conditions and congestion control

## 🐛 Troubleshooting

### Backend Issues
```bash
# Check if Flask server is running
curl http://localhost:5000/api/metrics/global

# View server logs
tail -f backend/logs/app.log

# Test metrics generation
python test_metrics.py
```

### Frontend Issues
```bash
# Check if React dev server is running
curl http://localhost:3000

# View browser console for errors
# Check network tab for API calls

# Rebuild frontend
cd frontend && npm run build
```

### Common Problems

1. **No metrics data**: Ensure backend is generating sample clients
2. **CORS errors**: Check CORS_ORIGINS in backend config
3. **Connection failed**: Verify backend server is running on port 5000
4. **Graphs not loading**: Check if recharts dependency is installed

## 🧪 Testing

### Run Test Suite
```bash
# Backend tests
cd backend && python -m pytest tests/

# Frontend tests  
cd frontend && npm test

# Integration test
python test_metrics.py
```

### Manual Testing
1. Open http://localhost:3000
2. Verify metrics dashboard loads
3. Check real-time updates every 2 seconds
4. Test time range selectors
5. Verify algorithm switching

## 🎨 Customization

### Adding New Algorithms
1. Create algorithm class in `backend/algorithms/`
2. Add to `AlgorithmType` enum in `tcp_congestion.py`
3. Update frontend algorithm tags in `CongestionGraph.jsx`

### Modifying Metrics Display
1. Edit `MetricsDashboard.jsx` for layout changes
2. Update `MetricsDashboard.css` for styling
3. Modify `NetworkStats.jsx` for new statistics

### Changing Update Intervals
- Backend: Modify sleep time in `generate_sample_metrics()`
- Frontend: Update intervals in `useMetrics.js` and service calls

## 📚 Learn More

- [TCP Congestion Control Algorithms](https://en.wikipedia.org/wiki/TCP_congestion_control)
- [React Hooks Documentation](https://reactjs.org/docs/hooks-intro.html)
- [Flask API Development](https://flask.palletsprojects.com/)
- [Recharts Documentation](https://recharts.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Your TCP File Transfer Metrics System is now ready! 🎉**

Open http://localhost:3000 to see the live metrics dashboard in action.
