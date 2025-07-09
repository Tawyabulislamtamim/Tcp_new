import React, { useState, useEffect } from 'react';
import FileExplorer from './components/FileExplorer/FileExplorer';
import MetricsDashboard from './components/MetricsDashboard/MetricsDashboard';
import apiService from './services/api';
import './App.css';

function App() {
  const [connectionStatus, setConnectionStatus] = useState('connecting'); // 'connecting', 'connected', 'disconnected'
  const [error, setError] = useState(null);

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
        retryTimeout = setTimeout(connectToServer, 5000); // Retry in 5 seconds
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
    // Future: preview or transfer functionality
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
    <div className="app">
      <header className="app-header">
        <h1>TCP File Transfer System</h1>
        <div className="connection-indicator">
          <span className="status-dot connected"></span>
          <span>Connected</span>
        </div>
      </header>

      <main className="app-main">
        <div className="app-layout">
          <div className="left-panel">
            <FileExplorer onFileSelect={handleFileSelect} />
          </div>
          <div className="right-panel">
            <MetricsDashboard />
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
