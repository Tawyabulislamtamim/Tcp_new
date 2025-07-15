import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import FileExplorer from './components/FileExplorer/FileExplorer';
import MetricsDashboard from './components/MetricsDashboard/MetricsDashboard';
import ControlPanel from './components/ControlPanel/ControlPanel';
import AlgorithmInsights from './components/AlgorithmInsights/AlgorithmInsights';
import apiService from './services/api';
import './App.css';




// --- Home Page ---
function HomePage({ onFileSelect }) {
  const navigate = useNavigate();

  return (
    <div className="app">
      <header className="app-header">
        <h1>TCP File Transfer System</h1>
         <button className="analysis-button" onClick={() => navigate('/analysis')}>
        📊 Analysis
      </button>
        <div className="connection-indicator">
          <span className="status-dot connected"></span>
          <span>Connected</span>
        </div>
      </header>
      
<main className="app-main">
  <div className="app-layout">
    <div className="left-panel">
      <FileExplorer onFileSelect={onFileSelect} />
     
    </div>
  </div>
</main>

    </div>
  );
}

// --- Analysis Page ---
function AnalysisPage({ globalMetrics, onMetricsUpdate }) {
  const navigate = useNavigate();

  return (
    <div className="app">
      <header className="app-header">
         <button className="back-button" onClick={() => navigate('/')}>
          ← Back
        </button>

       <button className="algorithm-selection-button" onClick={() => navigate('/algorithm-selection')}>
    ⚙️ Algorithm Selection Info
  </button>
        <h1>📈 Analysis Dashboard</h1>
      </header>
    <main className="app-main">
  <div className="dashboard-container">
    <div className="top-row">
      <ControlPanel />
    </div>
    
    <div className="content-column">
      <MetricsDashboard onMetricsUpdate={onMetricsUpdate} />
    </div>
  </div>
</main>



    </div>
  );
}

// --- App Component ---
function App() {
  const [connectionStatus, setConnectionStatus] = useState('connecting');
  const [error, setError] = useState(null);
  const [globalMetrics, setGlobalMetrics] = useState(null);

  useEffect(() => {
    let retryTimeout;

    const connectToServer = async () => {
      try {
        await apiService.connect();
        setConnectionStatus('connected');
        setError(null);
      } catch (err) {
        setConnectionStatus('disconnected');
        setError(err.message);
        retryTimeout = setTimeout(connectToServer, 5000);
      }
    };

    connectToServer();

    return () => {
      apiService.disconnect();
      clearTimeout(retryTimeout);
    };
  }, []);

  const handleFileSelect = (file) => {
    console.log('Selected file:', file);
  };

  if (connectionStatus === 'connecting') {
    return (
      <div className="app connecting">
        <div className="loading-spinner"></div>
        <p>Connecting to server...</p>
      </div>
    );
  }

  if (connectionStatus === 'disconnected') {
    return (
      <div className="app connecting">
        <div className="error-icon">⚠️</div>
        <h2>Connection Error</h2>
        <p>{error || 'Unable to connect to the server.'}</p>
        <p>Retrying in a few seconds...</p>
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage onFileSelect={handleFileSelect} />} />
        <Route path="/analysis" element={<AnalysisPage globalMetrics={globalMetrics} onMetricsUpdate={setGlobalMetrics} />} />
        <Route path="/algorithm-selection" element={<AlgorithmInsights globalMetrics={globalMetrics} />} />

      </Routes>
    </Router>
  );
}

export default App;
