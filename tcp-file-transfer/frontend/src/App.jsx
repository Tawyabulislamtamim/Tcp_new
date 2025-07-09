import React, { useState, useEffect } from 'react';
import FileExplorer from './components/FileExplorer/FileExplorer';
import apiService from './services/api';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize connection to backend
  useEffect(() => {
    const initialize = async () => {
      try {
        await apiService.connect();
        setIsConnected(true);
      } catch (err) {
        setError(err.message);
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };

    initialize();

    return () => {
      if (isConnected) {
        apiService.disconnect();
      }
    };
  }, []);

  const handleFileSelect = (file) => {
    console.log('Selected file:', file);
    // You can implement file preview or other actions here
  };

  if (loading) {
    return (
      <div className="app connecting">
        <div className="loading-spinner"></div>
        <p>Connecting to server...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app connecting">
        <div className="error-icon">⚠️</div>
        <h2>Connection Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>TCP File Transfer System</h1>
        <div className="connection-indicator">
          <span className="status-dot"></span>
          <span>Connected</span>
        </div>
      </header>

      <main className="app-main">
        <div className="app-layout">
          <div className="left-panel">
            <FileExplorer onFileSelect={handleFileSelect} />
          </div>
          <div className="right-panel">
            {/* You can add other components here like MetricsDashboard */}
            <div className="metrics-placeholder">
              <h2>Metrics Dashboard</h2>
              <p>Network metrics will appear here</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;