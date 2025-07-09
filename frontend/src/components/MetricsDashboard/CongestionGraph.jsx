import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CongestionGraph = ({ data, timespan }) => {
    // Process data for the chart
    const processedData = data.map(metric => ({
        time: new Date(metric.timestamp * 1000).toLocaleTimeString(),
        timestamp: metric.timestamp,
        cwnd: metric.cwnd,
        ssthresh: metric.ssthresh,
        bandwidth: metric.bandwidth / 1024, // Convert to KB/s
        rtt: metric.rtt,
        algorithm: metric.algorithm,
        client_id: metric.client_id
    }));

    // Sort by timestamp and take only recent data points
    const sortedData = processedData
        .sort((a, b) => a.timestamp - b.timestamp)
        .slice(-50); // Show last 50 data points

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="custom-tooltip">
                    <p className="tooltip-time">{`Time: ${label}`}</p>
                    <p className="tooltip-algorithm">{`Algorithm: ${data.algorithm}`}</p>
                    <p className="tooltip-client">{`Client: ${data.client_id}`}</p>
                    {payload.map((entry, index) => (
                        <p key={index} style={{ color: entry.color }}>
                            {`${entry.name}: ${entry.value.toFixed(2)}${getUnit(entry.dataKey)}`}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    const getUnit = (dataKey) => {
        switch (dataKey) {
            case 'bandwidth': return ' KB/s';
            case 'rtt': return ' ms';
            case 'cwnd':
            case 'ssthresh': return ' packets';
            default: return '';
        }
    };

    if (!data || data.length === 0) {
        return (
            <div className="congestion-graph no-data">
                <h3>Congestion Control Metrics</h3>
                <p>No data available. Start a file transfer to see metrics.</p>
            </div>
        );
    }

    return (
        <div className="congestion-graph">
            <h3>Congestion Control Metrics (Last {timespan < 60 ? `${timespan}s` : `${timespan/60}m`})</h3>
            
            {/* Congestion Window and Slow Start Threshold */}
            <div className="graph-container">
                <h4>Congestion Window & Slow Start Threshold</h4>
                <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={sortedData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                            dataKey="time" 
                            tick={{ fontSize: 12 }}
                            interval="preserveStartEnd"
                        />
                        <YAxis tick={{ fontSize: 12 }} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Line 
                            type="monotone" 
                            dataKey="cwnd" 
                            stroke="#2563eb" 
                            strokeWidth={2}
                            name="Congestion Window"
                            dot={false}
                        />
                        <Line 
                            type="monotone" 
                            dataKey="ssthresh" 
                            stroke="#dc2626" 
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            name="Slow Start Threshold"
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Bandwidth and RTT */}
            <div className="graph-container">
                <h4>Bandwidth & Round Trip Time</h4>
                <ResponsiveContainer width="100%" height={250}>
                    <LineChart data={sortedData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                            dataKey="time" 
                            tick={{ fontSize: 12 }}
                            interval="preserveStartEnd"
                        />
                        <YAxis yAxisId="bandwidth" orientation="left" tick={{ fontSize: 12 }} />
                        <YAxis yAxisId="rtt" orientation="right" tick={{ fontSize: 12 }} />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Line 
                            yAxisId="bandwidth"
                            type="monotone" 
                            dataKey="bandwidth" 
                            stroke="#059669" 
                            strokeWidth={2}
                            name="Bandwidth (KB/s)"
                            dot={false}
                        />
                        <Line 
                            yAxisId="rtt"
                            type="monotone" 
                            dataKey="rtt" 
                            stroke="#d97706" 
                            strokeWidth={2}
                            name="RTT (ms)"
                            dot={false}
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {/* Algorithm Distribution */}
            <div className="algorithm-info">
                <h4>Active Algorithms</h4>
                <div className="algorithm-list">
                    {Array.from(new Set(data.map(d => d.algorithm))).map(algorithm => (
                        <span key={algorithm} className={`algorithm-tag ${algorithm.toLowerCase()}`}>
                            {algorithm.toUpperCase()}
                        </span>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default CongestionGraph;
