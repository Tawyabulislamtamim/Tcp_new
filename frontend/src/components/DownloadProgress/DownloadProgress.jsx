import React from 'react';
import './DownloadProgress.css';

const DownloadProgress = ({ downloads, onClose, onRemoveDownload }) => {
    const cancelDownload = async (sessionId) => {
        try {
            await fetch(`/api/transfer/cancel-download/${sessionId}`, {
                method: 'POST'
            });
            
            onRemoveDownload(sessionId);
        } catch (error) {
            console.error('Cancel error:', error);
        }
    };

    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    };

    const formatTime = (seconds) => {
        if (!seconds || seconds === Infinity) return '--';
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    };

    // Expose function globally for FileExplorer to use
    // window.startMegaStyleDownload = startDownload;

    if (downloads.length === 0) return null;

    return (
        <div className="download-progress-overlay">
            <div className="download-progress-panel">
                <div className="panel-header">
                    <h3>📥 Downloads</h3>
                    <button onClick={onClose} className="close-button">×</button>
                </div>

                <div className="downloads-list">
                    {downloads.map((download) => (
                        <div key={download.sessionId} className={`download-item ${download.status}`}>
                            <div className="download-info">
                                <div className="file-name">{download.fileName}</div>
                                <div className="file-details">
                                    <span>{formatBytes(download.fileSize)}</span>
                                    {download.speed > 0 && (
                                        <>
                                            <span>•</span>
                                            <span>{download.speed.toFixed(1)} MB/s</span>
                                        </>
                                    )}
                                    {download.eta > 0 && (
                                        <>
                                            <span>•</span>
                                            <span>ETA: {formatTime(download.eta)}</span>
                                        </>
                                    )}
                                </div>
                            </div>

                            <div className="download-progress">
                                <div className="progress-bar">
                                    <div 
                                        className="progress-fill" 
                                        style={{ width: `${download.progress}%` }}
                                    ></div>
                                </div>
                                <div className="progress-text">
                                    {download.status === 'starting' && '🔄 Starting...'}
                                    {download.status === 'downloading' && `📊 ${download.progress.toFixed(1)}% - TCP Transfer in Progress`}
                                    {download.status === 'completed' && '⚡ Processing Complete - Preparing Download...'}
                                    {download.status === 'browser-downloading' && '💾 Saving to Downloads...'}
                                    {download.status === 'saved' && '✅ Saved to Downloads'}
                                    {download.status === 'error' && '❌ Error'}
                                </div>
                            </div>

                            <div className="download-actions">
                                {(download.status === 'downloading' || download.status === 'starting') && (
                                    <button 
                                        onClick={() => cancelDownload(download.sessionId)}
                                        className="cancel-button"
                                    >
                                        Cancel
                                    </button>
                                )}
                                {(download.status === 'saved' || download.status === 'error') && (
                                    <button 
                                        onClick={() => onRemoveDownload(download.sessionId)}
                                        className="remove-button"
                                    >
                                        Remove
                                    </button>
                                )}
                                {download.status === 'completed' && (
                                    <span className="status-info">Ready for download...</span>
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="panel-footer">
                    <small>Files are downloaded in your browser with real-time TCP metrics tracking</small>
                </div>
            </div>
        </div>
    );
};

export default DownloadProgress;
