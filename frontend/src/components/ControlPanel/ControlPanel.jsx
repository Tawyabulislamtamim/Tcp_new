import React, { useState, useEffect } from 'react';
import './ControlPanel.css';

const ControlPanel = () => {
    const [demoMode, setDemoMode] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');

    useEffect(() => {
        fetchDemoModeStatus();
    }, []);

    const fetchDemoModeStatus = async () => {
        try {
            const response = await fetch('/api/files/config/demo-mode');
            const data = await response.json();
            setDemoMode(data.demo_mode);
        } catch (error) {
            console.error('Failed to fetch demo mode status:', error);
        }
    };

    const toggleDemoMode = async () => {
        setIsLoading(true);
        setMessage('');

        try {
            const response = await fetch('/api/files/config/demo-mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    demo_mode: !demoMode
                })
            });

            const data = await response.json();
            if (response.ok) {
                setDemoMode(data.demo_mode);
                setMessage(data.message);
            } else {
                setMessage(`Error: ${data.error}`);
            }
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        } finally {
            setIsLoading(false);
            
            // Clear message after 3 seconds
            setTimeout(() => {
                setMessage('');
            }, 3000);
        }
    };

   return (
  <div className="control-panel-row">
    <div className="connection-types-box">
      <h4>📊 Connection Types</h4>
      <ul>
        <li>
          <span className="connection-type demo">🎭 Demo</span> - Simulated connections for testing TCP algorithms
        </li>
        <li>
          <span className="connection-type real">🚀 Real</span> - Actual file transfers and uploads
        </li>
      </ul>
    </div>

    <div className="demo-toggle-box">
      <div className="toggle-info">
        <h4>Demo Mode</h4>
        <p>
          {demoMode
            ? "Simulated connections are active for demonstration"
            : "Only real file transfers will show connections"}
        </p>
      </div>
      <label className="toggle-switch">
        <input
          type="checkbox"
          checked={demoMode}
          onChange={toggleDemoMode}
          disabled={isLoading}
        />
        <span className="toggle-slider"></span>
      </label>
    </div>
  </div>
);


};

export default ControlPanel;
