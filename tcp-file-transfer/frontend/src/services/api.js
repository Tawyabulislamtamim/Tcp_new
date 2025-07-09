// frontend/src/services/api.js
class APIService {
    constructor() {
        this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
        this.connected = false;
    }

    async connect() {
        try {
            const response = await fetch(`${this.baseURL}/health`);
            if (!response.ok) {
                throw new Error('Connection failed');
            }
            this.connected = true;
            return await response.json();
        } catch (error) {
            this.connected = false;
            throw new Error(`Failed to connect to server: ${error.message}`);
        }
    }

    disconnect() {
        this.connected = false;
    }

    async listFiles(path = '') {
        try {
            const response = await fetch(`${this.baseURL}/files/list?path=${encodeURIComponent(path)}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to list files: ${error.message}`);
        }
    }

    async downloadFile(filePath, onProgress) {
        try {
            const response = await fetch(`${this.baseURL}/files/download?path=${encodeURIComponent(filePath)}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const contentLength = response.headers.get('content-length');
            const total = parseInt(contentLength, 10);
            let loaded = 0;

            const reader = response.body.getReader();
            const chunks = [];

            while (true) {
                const { done, value } = await reader.read();
                
                if (done) break;
                
                chunks.push(value);
                loaded += value.length;
                
                if (onProgress && total) {
                    onProgress(loaded / total);
                }
            }

            return new Blob(chunks);
        } catch (error) {
            throw new Error(`Failed to download file: ${error.message}`);
        }
    }

    async getClientMetrics() {
        try {
            const response = await fetch(`${this.baseURL}/metrics/client`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get client metrics: ${error.message}`);
        }
    }

    async getGlobalMetrics() {
        try {
            const response = await fetch(`${this.baseURL}/metrics/global`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            throw new Error(`Failed to get global metrics: ${error.message}`);
        }
    }
}

export default new APIService();