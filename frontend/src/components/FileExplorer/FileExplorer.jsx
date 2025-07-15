import React, { useState, useEffect } from 'react';
import {
  Folder, File, Download, Loader2, AlertCircle
} from 'lucide-react';
import { FiSearch, FiFilter, FiLock } from 'react-icons/fi';

import { formatFileSize, formatDate } from '../../utils/formatters';
import apiService from '../../services/api';
import FileUpload from '../FileUpload/FileUpload';
import DownloadProgress from '../DownloadProgress/DownloadProgress';

import './FileExplorer.css';

const FileExplorer = ({ onFileSelect }) => {
  const [currentPath, setCurrentPath] = useState('');
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(null);
  const [uploadError, setUploadError] = useState(null);
  const [downloadSessions, setDownloadSessions] = useState([]);
  const [showDownloadProgress, setShowDownloadProgress] = useState(false);
  const [clientId, setClientId] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [totalSize, setTotalSize] = useState(0);

  const [showAllFiles, setShowAllFiles] = useState(false);
  const FILES_PREVIEW_COUNT = 10;

  useEffect(() => {
    const getClientId = async () => {
      try {
        const response = await apiService.connect();
        setClientId(response.client_id);
      } catch (error) {
        setError(`Connection failed: ${error.message}`);
      }
    };
    getClientId();
  }, []);

  useEffect(() => {
    fetchFiles(currentPath);
  }, [currentPath]);

  useEffect(() => {
    const fetchTotalSize = async () => {
      try {
        const data = await apiService.listFiles('');
        const sum = data.files.reduce((acc, f) => acc + (f.size || 0), 0);
        setTotalSize(sum);
      } catch {
        setTotalSize(0);
      }
    };
    fetchTotalSize();
  }, [files]);

  const fetchFiles = async (path) => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await apiService.listFiles(path);
      setFiles(data.files);
    } catch (err) {
      setError(err.message);
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToDirectory = (path) => setCurrentPath(path);

  const handleFileClick = (file) => {
    if (file.is_directory) navigateToDirectory(file.path);
    else if (onFileSelect) onFileSelect(file);
  };

  const handleDownload = async (file, e) => {
    e.stopPropagation();
    if (!clientId) {
      try {
        const response = await apiService.connect();
        setClientId(response.client_id);
      } catch (error) {
        setError(`Connection failed: ${error.message}`);
        return;
      }
    }

    try {
      setShowDownloadProgress(true);
      await startDownload(file.path, file.name, clientId);
    } catch (err) {
      setError(err.message);
    }
  };

  const startDownload = async (filePath, fileName, clientId) => {
    const sessionData = await apiService.startDownloadSession(filePath, clientId);
    const newDownload = {
      sessionId: sessionData.session_id,
      fileName: sessionData.file_name,
      fileSize: sessionData.file_size,
      clientId: sessionData.client_id,
      progress: 0, speed: 0, eta: 0,
      status: 'starting',
      startTime: Date.now()
    };
    setDownloadSessions(prev => [...prev, newDownload]);
    triggerBrowserDownload(newDownload.sessionId);
    trackDownloadProgress(newDownload.sessionId);
  };

  const triggerBrowserDownload = (sessionId) => {
    const link = document.createElement('a');
    const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
    link.href = `${baseURL}/transfer/stream-download/${sessionId}`;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    setTimeout(() => document.body.removeChild(link), 100);
  };

  const trackDownloadProgress = async (sessionId) => {
    const poll = async () => {
      try {
        const progress = await apiService.getDownloadProgress(sessionId);
        setDownloadSessions(prev => prev.map(download =>
          download.sessionId === sessionId
            ? {
              ...download,
              progress: progress.progress_percent,
              speed: progress.speed_mbps,
              eta: progress.eta_seconds,
              status: progress.is_complete ? 'completed' : 'downloading'
            }
            : download
        ));
        if (!progress.is_complete) {
          setTimeout(poll, 500);
        }
      } catch (error) {
        setDownloadSessions(prev => prev.map(download =>
          download.sessionId === sessionId
            ? { ...download, status: 'error', error: error.message }
            : download
        ));
      }
    };
    poll();
  };

  const handleUploadSuccess = (res) => {
    setUploadSuccess(`Successfully uploaded ${res.filename}`);
    setUploadError(null);
    fetchFiles(currentPath);
    setTimeout(() => setUploadSuccess(null), 5000);
  };

  const handleUploadError = (err) => {
    setUploadError(err);
    setUploadSuccess(null);
    setTimeout(() => setUploadError(null), 7000);
  };

  const handleSearchChange = async (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (!query.trim()) return setSearchResults(null);

    try {
      const data = await apiService.listFiles(currentPath);
      const matches = data.files.filter(f =>
        f.name.toLowerCase().includes(query.toLowerCase())
      );
      setSearchResults(matches);
    } catch {
      setSearchResults([]);
    }
  };

  const displayedFiles = searchResults ?? files;

  const visibleFiles = showAllFiles
    ? displayedFiles
    : displayedFiles.slice(0, FILES_PREVIEW_COUNT);

  if (error) {
    return (
      <div className="file-explorer error">
        <AlertCircle size={48} className="text-red-500 mb-4" />
        <h3>Error Loading Files</h3>
        <p>{error}</p>
        <button onClick={() => fetchFiles(currentPath)}>Retry</button>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="file-explorer loading">
        <Loader2 size={48} className="animate-spin text-blue-500 mb-4" />
        <p>Loading files...</p>
      </div>
    );
  }

  return (
    <div className="file-explorer">
      <div className="file-manager-header">
        <div className="left-section">
          <h2>File Manager</h2>
          <div className="search-filter-group">
            <div className="search-box">
              <FiSearch className="search-icon" />
              <input
                type="text"
                placeholder="Search files…"
                value={searchQuery}
                onChange={handleSearchChange}
              />
            </div>
            <button className="filter-button">
              <FiFilter className="filter-icon" /> Filter
            </button>
          </div>
        </div>
        <div className="right-section">
          <div className="storage-indicator">
            <FiLock /> <span>{formatFileSize(totalSize)} / 10 GB</span>
          </div>
        </div>
      </div>

      <div className="recent-files-label">Recent Files</div>

      {displayedFiles.length === 0 ? (
        <div className="empty-directory">
          <Folder size={48} />
          <h3>No files found</h3>
        </div>
      ) : (
        <>
          <div className="file-list">
            {visibleFiles.map((file) => (
              <div
                key={file.path}
                onClick={() => handleFileClick(file)}
                className={`file-item list-view ${file.is_directory ? 'directory' : ''}`}
              >
                <div className="file-icon">
                  {file.is_directory ? <Folder size={24} /> : <File size={24} />}
                </div>
                <div className="file-info">
                  <div className="file-name">{file.name}</div>
                  <div className="file-details">
                    <span>{formatFileSize(file.size)}</span>
                    <span>{formatDate(file.modified_time)}</span>
                  </div>
                </div>
                {!file.is_directory && (
                  <button
                    onClick={(e) => handleDownload(file, e)}
                    className="download-button modern-download"
                    title={`Download ${file.name}`}
                  >
                    <Download size={16} />
                    <span className="download-text">Download</span>
                  </button>
                )}
              </div>
            ))}
          </div>

          {displayedFiles.length > FILES_PREVIEW_COUNT && (
            <div className="file-list-toggle">
              {showAllFiles ? (
                <button onClick={() => setShowAllFiles(false)}>Show Less</button>
              ) : (
                <button onClick={() => setShowAllFiles(true)}>See More</button>
              )}
            </div>
          )}
        </>
      )}

      <FileUpload
        currentPath={currentPath}
        onUploadSuccess={handleUploadSuccess}
        onUploadError={handleUploadError}
      />

      {uploadSuccess && <div className="upload-feedback success">{uploadSuccess}</div>}
      {uploadError && <div className="upload-feedback error">{uploadError}</div>}

      {showDownloadProgress && downloadSessions.length > 0 && (
        <DownloadProgress
          downloads={downloadSessions}
          onClose={() => setShowDownloadProgress(false)}
          onRemoveDownload={(id) =>
            setDownloadSessions((prev) => prev.filter((d) => d.sessionId !== id))
          }
        />
      )}
    </div>
  );
};

export default FileExplorer;
