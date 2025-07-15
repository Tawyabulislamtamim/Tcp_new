import { useState, useEffect } from 'react';
import metricsService from '../services/metricsService';

export const useMetrics = (clientId, refreshInterval = 1000) => {
    const [metrics, setMetrics] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let intervalId;
        
        const fetchMetrics = async () => {
            try {
                setIsLoading(true);
                const data = clientId 
                    ? await metricsService.getClientMetrics(clientId) 
                    : await metricsService.getGlobalMetrics();
                setMetrics(data);
                setError(null);
            } catch (err) {
                setError(err.message);
                console.error('Failed to fetch metrics:', err);
            } finally {
                setIsLoading(false);
            }
        };

        // Initial fetch
        fetchMetrics();
        
        // Set up polling if refreshInterval is provided
        if (refreshInterval > 0) {
            intervalId = setInterval(fetchMetrics, refreshInterval);
        }

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    }, [clientId, refreshInterval]);

    return { metrics, isLoading, error };
};