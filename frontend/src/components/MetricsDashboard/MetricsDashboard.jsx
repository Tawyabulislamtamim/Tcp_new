import React, { useState, useEffect } from 'react';
import { useMetrics } from '../../hooks/useMetrics';
import CongestionGraph from './CongestionGraph';
import NetworkStats from './NetworkStats';
import metricsService from '../../services/metricsService';
import './MetricsDashboard.css';

const MetricsDashboard = () => {
    const [globalMetrics, setGlobalMetrics] = useState(null);
    const [metricsHistory, setMetricsHistory] = useState([]);
    const [selectedTimespan, setSelectedTimespan] = useState(30);
    const [isConnected, setIsConnected] = useState(false);
    const [error, setError] = useState(null);

    // Fetch global metrics
    const { metrics: fetchedGlobalMetrics, isLoading, error: fetchError } = useMetrics(null, 2000);

    useEffect(() => {
        if (fetchedGlobalMetrics) {
            setGlobalMetrics(fetchedGlobalMetrics);
            setError(null);
        }
        if (fetchError) {
            setError(fetchError);
        }
    }, [fetchedGlobalMetrics, fetchError]);

    // Fetch metrics history
    useEffect(() => {
        const fetchHistory = async () => {
            try {
                const history = await metricsService.getMetricsHistory(selectedTimespan);
                setMetricsHistory(history);
            } catch (err) {
                console.error('Failed to fetch metrics history:', err);
            }
        };

        fetchHistory();
        const interval = setInterval(fetchHistory, 3000); // Update every 3 seconds

        return () => clearInterval(interval);
    }, [selectedTimespan]);

    // Subscribe to real-time metrics updates
    useEffect(() => {
        const unsubscribe = metricsService.subscribeToMetrics((data) => {
            if (data.error) {
                setError(data.error);
                setIsConnected(false);
            } else {
                setGlobalMetrics(data);
                setIsConnected(true);
                setError(null);
            }
        });

        return unsubscribe;
    }, []);

    const handleTimespanChange = (newTimespan) => {
        setSelectedTimespan(newTimespan);
    };

    if (isLoading && !globalMetrics) {
        return (
            <div className="metrics-dashboard loading">
                <div className="loading-spinner"></div>
                <p>Loading metrics...</p>
            </div>
        );
    }

    return (
        <div className="metrics-dashboard">
            <div className="dashboard-header">
                <h2>Network Metrics Dashboard</h2>
                <div className="connection-status">
                    <span className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`}></span>
                    <span>{isConnected ? 'Live' : 'Disconnected'}</span>
                </div>
            </div>

            {error && (
                <div className="error-banner">
                    <span>⚠️ {error}</span>
                </div>
            )}

            <div className="dashboard-content">
                {/* Global Network Stats */}
                <div className="stats-section">
                    <NetworkStats metrics={globalMetrics} />
                </div>

                {/* Time Range Selector */}
                <div className="timespan-selector">
                    <label>View Last:</label>
                    {[30, 60, 120, 300].map(seconds => (
                        <button
                            key={seconds}
                            className={selectedTimespan === seconds ? 'active' : ''}
                            onClick={() => handleTimespanChange(seconds)}
                        >
                            {seconds < 60 ? `${seconds}s` : `${seconds / 60}m`}
                        </button>
                    ))}
                </div>

                {/* Congestion Control Graph */}
                <div className="graph-section">
                    <CongestionGraph 
                        data={metricsHistory} 
                        timespan={selectedTimespan}
                    />
                </div>

                {/* Additional Statistics */}
                {globalMetrics && (
                    <div className="additional-stats">
                        <div className="stat-card">
                            <h4>Total Data Transferred</h4>
                            <p>{formatBytes(globalMetrics.total_bytes_transferred || 0)}</p>
                        </div>
                        <div className="stat-card">
                            <h4>Average RTT</h4>
                            <p>{(globalMetrics.average_rtt || 0).toFixed(2)} ms</p>
                        </div>
                        <div className="stat-card">
                            <h4>Total Packet Loss</h4>
                            <p>{(globalMetrics.total_packet_loss || 0).toFixed(4)}%</p>
                        </div>
                        <div className="stat-card">
                            <h4>Current Bandwidth</h4>
                            <p>{formatBandwidth(globalMetrics.total_bandwidth || 0)}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// Utility functions
const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

const formatBandwidth = (bytesPerSec) => {
    if (bytesPerSec === 0) return '0 B/s';
    const k = 1024;
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    const i = Math.floor(Math.log(bytesPerSec) / Math.log(k));
    return parseFloat((bytesPerSec / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export default MetricsDashboard;
