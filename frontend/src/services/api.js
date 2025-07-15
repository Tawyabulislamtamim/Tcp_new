// frontend/src/services/api.js
class APIService {
    constructor() {
        this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
        this.connected = false;
        this.clientId = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.retryDelay = 1000;
        this.eventSource = null;
    }

    async _fetchWithRetry(url, options = {}, retries = this.maxRetries) {
        try {
            const response = await fetch(url, {
                ...options,
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                    ...(options.headers || {})
                }
            });

            if (!response.ok) {
                if (response.status === 401 && retries > 0) {
                    await this.connect();
                    return this._fetchWithRetry(url, options, retries - 1);
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.retryCount = 0;
            return response;
        } catch (error) {
            if (retries > 0) {
                await new Promise(resolve => setTimeout(resolve, this.retryDelay * (this.maxRetries - retries + 1)));
                return this._fetchWithRetry(url, options, retries - 1);
            }
            throw error;
        }
    }

    async connect() {
        try {
            const healthResponse = await this._fetchWithRetry(`${this.baseURL}/health`);
            const healthData = await healthResponse.json();

            if (!this.clientId) {
                const connectResponse = await this._fetchWithRetry(`${this.baseURL}/connect`, {
                    method: 'POST'
                });
                const connectData = await connectResponse.json();
                this.clientId = connectData.client_id;
            }

            this.connected = true;
            // Return connection data instead of health data
            return {
                connected: true,
                client_id: this.clientId,
                health: healthData
            };
        } catch (error) {
            this.connected = false;
            this.clientId = null;
            throw new Error(`Failed to connect to server: ${error.message}`);
        }
    }

    async disconnect() {
        if (!this.clientId) return;

        try {
            await this._fetchWithRetry(`${this.baseURL}/disconnect`, {
                method: 'POST',
                body: JSON.stringify({ client_id: this.clientId })
            });
        } catch (error) {
            console.error('Disconnection error:', error);
        } finally {
            if (this.eventSource) {
                this.eventSource.close();
                this.eventSource = null;
            }
            this.connected = false;
            this.clientId = null;
        }
    }

    async listFiles(path = '') {
        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/files/list?path=${encodeURIComponent(path)}`
            );
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to list files: ${error.message}`);
        }
    }

    async downloadFile(filePath, onProgress) {
        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/files/download?path=${encodeURIComponent(filePath)}`
            );

            const contentLength = response.headers.get('content-length');
            const total = parseInt(contentLength, 10) || 0;
            let loaded = 0;

            const reader = response.body.getReader();
            const chunks = [];

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                chunks.push(value);
                loaded += value.length;
                if (onProgress && total > 0) {
                    onProgress(loaded / total);
                }
            }

            return new Blob(chunks);
        } catch (error) {
            throw new Error(`Failed to download file: ${error.message}`);
        }
    }

    async getClientMetrics(clientId = this.clientId) {
        if (!clientId) throw new Error('No client ID available');

        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/metrics/client/${clientId}`
            );
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get client metrics: ${error.message}`);
        }
    }

    async getGlobalMetrics() {
        try {
            const response = await this._fetchWithRetry(`${this.baseURL}/metrics/global`);
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get global metrics: ${error.message}`);
        }
    }

    async subscribeToMetrics(callback) {
        if (!this.clientId) {
            throw new Error('No client ID available');
        }

        if (this.eventSource) {
            this.eventSource.close();
        }

        return new Promise((resolve, reject) => {
            try {
                this.eventSource = new EventSource(
                    `${this.baseURL}/metrics/stream?client_id=${this.clientId}`
                );

                this.eventSource.onopen = () => {
                    console.log('SSE connection established');
                    resolve(() => {
                        if (this.eventSource) {
                            this.eventSource.close();
                            this.eventSource = null;
                        }
                    });
                };

                this.eventSource.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        callback(data);
                    } catch (err) {
                        console.error('Error parsing SSE data:', err);
                    }
                };

                this.eventSource.onerror = (err) => {
                    console.error('SSE connection error:', err);
                    if (this.eventSource) {
                        this.eventSource.close();
                        this.eventSource = null;
                    }
                    reject(err);
                    setTimeout(() => this.subscribeToMetrics(callback), 5000);
                };
            } catch (error) {
                reject(error);
            }
        });
    }

    async startTransfer(filePath) {
        if (!this.clientId) throw new Error('No client ID available');

        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/transfer/download?path=${encodeURIComponent(filePath)}&client_id=${this.clientId}`
            );
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to start transfer: ${error.message}`);
        }
    }

    async startDownloadSession(filePath, clientId) {
        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/transfer/start-download`, 
                {
                    method: 'POST',
                    body: JSON.stringify({
                        path: filePath,
                        client_id: clientId
                    })
                }
            );
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to start download session: ${error.message}`);
        }
    }

    async getDownloadProgress(sessionId) {
        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/transfer/download-progress/${sessionId}`
            );
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get download progress: ${error.message}`);
        }
    }

    async getTransferStatus(transferId) {
        try {
            const response = await this._fetchWithRetry(
                `${this.baseURL}/transfer/status/${transferId}`
            );
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get transfer status: ${error.message}`);
        }
    }

    // Add method to fetch metrics history
    async getMetricsHistory(seconds = 30) {
        try {
            const url = `${this.baseURL}/metrics/history?seconds=${seconds}`;
            const response = await this._fetchWithRetry(url);
            const data = await response.json();
            return data.metrics;
        } catch (error) {
            throw new Error(`Failed to get metrics history: ${error.message}`);
        }
    }
}

const apiService = new APIService();

// Auto-connect with retry logic
const initializeConnection = async () => {
    try {
        await apiService.connect();
        console.log('Successfully connected to server');
    } catch (error) {
        console.error('Initial connection failed, retrying...', error.message);
        setTimeout(initializeConnection, 5000);
    }
};

initializeConnection();

export default apiService;
