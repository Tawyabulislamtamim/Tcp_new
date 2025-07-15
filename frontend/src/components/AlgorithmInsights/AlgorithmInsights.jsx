import React, { useState, useEffect } from 'react';
import './AlgorithmInsights.css';

const AlgorithmInsights = ({ globalMetrics }) => {
    const [algorithmStats, setAlgorithmStats] = useState({});
    const [networkConditions, setNetworkConditions] = useState([]);

    useEffect(() => {
        // Process metrics to show algorithm performance
        if (globalMetrics && globalMetrics.clients) {
            const stats = {};
            const conditions = [];
            
            Object.values(globalMetrics.clients).forEach(client => {
                const algorithm = client.algorithm || 'unknown';
                if (!stats[algorithm]) {
                    stats[algorithm] = {
                        count: 0,
                        avgRtt: 0,
                        avgBandwidth: 0,
                        packetLoss: 0,
                        condition: 'unknown'
                    };
                }
                
                stats[algorithm].count++;
                stats[algorithm].avgRtt += client.rtt || 0;
                stats[algorithm].avgBandwidth += client.bandwidth || 0;
                stats[algorithm].packetLoss += client.packet_loss || 0;
                
                if (client.network_condition) {
                    conditions.push({
                        algorithm,
                        condition: client.network_condition,
                        rtt: client.rtt,
                        bandwidth: client.bandwidth,
                        loss: client.packet_loss,
                        clientId: client.client_id
                    });
                }
            });
            
            // Calculate averages
            Object.keys(stats).forEach(algo => {
                const count = stats[algo].count;
                if (count > 0) {
                    stats[algo].avgRtt /= count;
                    stats[algo].avgBandwidth /= count;
                    stats[algo].packetLoss /= count;
                }
            });
            
            setAlgorithmStats(stats);
            setNetworkConditions(conditions);
        }
    }, [globalMetrics]);

    const getAlgorithmInfo = (algorithm) => {
        const info = {
            'reno': {
                name: 'TCP Reno',
                icon: '🔄',
                color: 'blue',
                description: 'Fast recovery, moderate congestion handling',
                bestFor: 'General purpose, moderate congestion',
                research: 'Good balance between performance and fairness'
            },
            'cubic': {
                name: 'TCP CUBIC',
                icon: '📈',
                color: 'green',
                description: 'High-speed, long-distance optimization',
                bestFor: 'High bandwidth, low loss networks',
                research: 'Default in Linux, optimized for modern networks'
            },
            'tahoe': {
                name: 'TCP Tahoe',
                icon: '🛡️',
                color: 'orange',
                description: 'Conservative, stable congestion control',
                bestFor: 'High congestion, frequent packet loss',
                research: 'Most stable under heavy congestion'
            },
            'bbr': {
                name: 'TCP BBR',
                icon: '🚀',
                color: 'purple',
                description: 'Bandwidth-based, loss-resistant',
                bestFor: 'Wireless, lossy networks',
                research: 'Maintains throughput under random loss'
            }
        };
        return info[algorithm] || {
            name: algorithm.toUpperCase(),
            icon: '❓',
            color: 'gray',
            description: 'Unknown algorithm',
            bestFor: 'Unknown',
            research: 'No data available'
        };
    };

    const getConditionBadge = (condition) => {
        const badges = {
            'excellent': { text: 'Excellent', color: 'green', icon: '✨' },
            'good': { text: 'Good', color: 'blue', icon: '👍' },
            'congested': { text: 'Congested', color: 'orange', icon: '⚠️' },
            'lossy': { text: 'Lossy', color: 'red', icon: '📡' },
            'high_bw': { text: 'High BW', color: 'purple', icon: '🏎️' }
        };
        return badges[condition] || { text: condition, color: 'gray', icon: '❓' };
    };

    return (
        <div className="algorithm-insights">
            <h3>🧠 Intelligent TCP Algorithm Selection</h3>
            
            <div className="insights-section">
                <h4>📊 Active Algorithms</h4>
                <div className="algorithm-grid">
                    {Object.entries(algorithmStats).map(([algorithm, stats]) => {
                        const info = getAlgorithmInfo(algorithm);
                        return (
                            <div key={algorithm} className={`algorithm-card ${info.color}`}>
                                <div className="algorithm-header">
                                    <span className="algorithm-icon">{info.icon}</span>
                                    <div className="algorithm-name">
                                        <h5>{info.name}</h5>
                                        <span className="algorithm-count">{stats.count} connections</span>
                                    </div>
                                </div>
                                
                                <div className="algorithm-metrics">
                                    <div className="metric">
                                        <span className="metric-label">Avg RTT:</span>
                                        <span className="metric-value">{stats.avgRtt.toFixed(1)}ms</span>
                                    </div>
                                    <div className="metric">
                                        <span className="metric-label">Bandwidth:</span>
                                        <span className="metric-value">{(stats.avgBandwidth / 1024 / 1024).toFixed(1)}MB/s</span>
                                    </div>
                                    <div className="metric">
                                        <span className="metric-label">Loss Rate:</span>
                                        <span className="metric-value">{(stats.packetLoss * 100).toFixed(2)}%</span>
                                    </div>
                                </div>
                                
                                <div className="algorithm-info">
                                    <p className="best-for">{info.bestFor}</p>
                                    <p className="research-note">{info.research}</p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="insights-section">
                <h4>🌐 Network Conditions & Algorithm Switching</h4>
                <div className="conditions-list">
                    {networkConditions.map((item, index) => {
                        const badge = getConditionBadge(item.condition);
                        const info = getAlgorithmInfo(item.algorithm);
                        
                        return (
                            <div key={index} className="condition-item">
                                <div className="condition-header">
                                    <span className={`condition-badge ${badge.color}`}>
                                        {badge.icon} {badge.text}
                                    </span>
                                    <span className={`algorithm-badge ${info.color}`}>
                                        {info.icon} {info.name}
                                    </span>
                                </div>
                                
                                <div className="condition-details">
                                    <span>RTT: {item.rtt?.toFixed(1)}ms</span>
                                    <span>BW: {((item.bandwidth || 0) / 1024 / 1024).toFixed(1)}MB/s</span>
                                    <span>Loss: {((item.loss || 0) * 100).toFixed(2)}%</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="insights-section">
                <h4>🔬 Research-Based Switching Logic</h4>
                <div className="research-info">
                    <div className="switching-rule">
                        <strong>High Loss (&gt;2%) + Low RTT:</strong> → Reno (fast recovery)
                    </div>
                    <div className="switching-rule">
                        <strong>High Loss (&gt;2%) + High RTT:</strong> → Tahoe (stability)
                    </div>
                    <div className="switching-rule">
                        <strong>High BDP (BW×RTT &gt; 1000):</strong> → CUBIC (long fat networks)
                    </div>
                    <div className="switching-rule">
                        <strong>Wireless/Random Loss (0.1%-1%):</strong> → BBR (loss tolerance)
                    </div>
                    <div className="switching-rule">
                        <strong>Low Loss + Low RTT:</strong> → CUBIC (high throughput)
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AlgorithmInsights;
