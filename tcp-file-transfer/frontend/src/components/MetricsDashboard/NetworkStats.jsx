// frontend/src/components/MetricsDashboard/NetworkStats.jsx
import React from 'react';
import { formatSpeed } from '../../utils/formatters';

const NetworkStats = ({ clientMetrics }) => {
    if (!clientMetrics) {
        return (
            <div className="network-stats">
                <h3>Client Network Statistics</h3>
                <p>Loading client metrics...</p>
            </div>
        );
    }

    return (
        <div className="network-stats">
            <h3>Client Network Statistics</h3>
            <div className="stats-grid">
                <div className="stat-item">
                    <span className="stat-label">Algorithm</span>
                    <span className="stat-value">{clientMetrics.algorithm?.toUpperCase() || 'N/A'}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">CWND</span>
                    <span className="stat-value">{clientMetrics.cwnd?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">SSThresh</span>
                    <span className="stat-value">{clientMetrics.ssthresh?.toFixed(2) || 'N/A'}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">RTT</span>
                    <span className="stat-value">{clientMetrics.rtt?.toFixed(3)}s</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">Bandwidth</span>
                    <span className="stat-value">{formatSpeed(clientMetrics.bandwidth || 0)}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">Packet Loss</span>
                    <span className="stat-value">{((clientMetrics.packet_loss || 0) * 100).toFixed(2)}%</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">State</span>
                    <span className="stat-value">{clientMetrics.state || 'N/A'}</span>
                </div>
                <div className="stat-item">
                    <span className="stat-label">Duplicate ACKs</span>
                    <span className="stat-value">{clientMetrics.duplicate_acks || 0}</span>
                </div>
            </div>
        </div>
    );
};

export default NetworkStats;