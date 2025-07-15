import api from './api';

const metricsService = {
    async getGlobalMetrics() {
        // Use APIService to fetch global metrics
        try {
            return await api.getGlobalMetrics();
        } catch (error) {
            throw new Error(error.message || 'Failed to fetch global metrics');
        }
    },

    async getClientMetrics(clientId) {
        // Use APIService to fetch client-specific metrics
        try {
            return await api.getClientMetrics(clientId);
        } catch (error) {
            throw new Error(error.message || 'Failed to fetch client metrics');
        }
    },

    async getMetricsHistory(seconds = 30) {
        // Use APIService to fetch metrics history
        try {
            return await api.getMetricsHistory(seconds);
        } catch (error) {
            throw new Error(error.message || 'Failed to fetch metrics history');
        }
    },

    subscribeToMetrics(callback) {
        const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
        const eventSource = new EventSource(`${baseURL}/metrics/stream`);
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                callback(data);
            } catch (err) {
                console.error('Error parsing SSE data:', err);
            }
        };

        eventSource.onerror = (err) => {
            console.error('SSE error:', err);
            eventSource.close();
        };

        return () => eventSource.close();
    }
};

export default metricsService;