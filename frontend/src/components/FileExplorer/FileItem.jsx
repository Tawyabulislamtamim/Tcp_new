import React, { useState } from 'react';
import api from '../../services/api';
import { formatFileSize } from '../../utils/formatters';

const FileItem = ({ file, onDownloadStart, onDownloadComplete, onError }) => {
    const [isDownloading, setIsDownloading] = useState(false);
    const [progress, setProgress] = useState(0);

    const handleDownload = async () => {
        try {
            setIsDownloading(true);
            onDownloadStart(file.name);
            
            const blob = await api.downloadFile(file.path, (p) => {
                setProgress(p * 100);
            });

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = file.name;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            
            onDownloadComplete(file.name);
        } catch (error) {
            onError(file.name, error.message);
        } finally {
            setIsDownloading(false);
            setProgress(0);
        }
    };

    return (
        <div className={`file-item ${file.is_directory ? 'directory' : ''}`}>
            <div className="file-info">
                <div className="file-name">{file.name}</div>
                <div className="file-details">
                    <span>{formatFileSize(file.size)}</span>
                </div>
                {!file.is_directory && (
                    <button 
                        className="download-button" 
                        onClick={handleDownload}
                        disabled={isDownloading}
                    >
                        {isDownloading ? `${progress.toFixed(1)}%` : 'Download'}
                    </button>
                )}
            </div>
        </div>
    );
};

export default FileItem;