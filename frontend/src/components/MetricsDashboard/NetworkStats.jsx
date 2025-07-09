import React from 'react';

const NetworkStats = ({ metrics }) => {
    if (!metrics) {
        return (
            <div className="network-stats loading">
                <h3>Network Statistics</h3>
                <p>Loading statistics...</p>
            </div>
        );
    }

    const stats = [
        {
            label: 'Active Connections',
            value: metrics.active_connections || 0,
            unit: '',
            icon: '🔗',
            color: 'blue'
        },
        {
            label: 'Total Bandwidth',
            value: formatBandwidth(metrics.total_bandwidth || 0),
            unit: '',
            icon: '📊',
            color: 'green'
        },
        {
            label: 'Average RTT',
            value: (metrics.average_rtt || 0).toFixed(2),
            unit: 'ms',
            icon: '⏱️',
            color: 'orange'
        },
        {
            label: 'Data Transferred',
            value: formatBytes(metrics.total_bytes_transferred || 0),
            unit: '',
            icon: '💾',
            color: 'purple'
        }
    ];

    return (
        <div className="network-stats">
            <h3>Network Statistics</h3>
            <div className="stats-grid">
                {stats.map((stat, index) => (
                    <div key={index} className={`stat-item ${stat.color}`}>
                        <div className="stat-icon">{stat.icon}</div>
                        <div className="stat-content">
                            <div className="stat-value">
                                {stat.value}
                                {stat.unit && <span className="stat-unit">{stat.unit}</span>}
                            </div>
                            <div className="stat-label">{stat.label}</div>
                        </div>
                    </div>
                ))}
            </div>
            
            {/* Real-time indicator */}
            <div className="real-time-indicator">
                <span className="pulse-dot"></span>
                <span>Real-time updates</span>
                <small>Last updated: {new Date().toLocaleTimeString()}</small>
            </div>
        </div>
    );
};

// Utility functions
const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

const formatBandwidth = (bytesPerSec) => {
    if (bytesPerSec === 0) return '0 B/s';
    const k = 1024;
    const sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s'];
    const i = Math.floor(Math.log(bytesPerSec) / Math.log(k));
    return parseFloat((bytesPerSec / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

export default NetworkStats;