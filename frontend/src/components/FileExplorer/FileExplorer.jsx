import React, { useState, useEffect } from 'react';
import { Folder, File, ChevronLeft, Download, Loader2, AlertCircle } from 'lucide-react';
import { formatFileSize, formatDate } from '../../utils/formatters';
import apiService from '../../services/api';
import './FileExplorer.css';

const FileExplorer = ({ onFileSelect }) => {
  const [currentPath, setCurrentPath] = useState('');
  const [files, setFiles] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [breadcrumbs, setBreadcrumbs] = useState([]);

  useEffect(() => {
    fetchFiles(currentPath);
  }, [currentPath]);

  const fetchFiles = async (path) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const data = await apiService.listFiles(path);
      setFiles(data.files);
      
      // Generate breadcrumbs
      const pathParts = path.split('/').filter(Boolean);
      const crumbs = [];
      let accumulatedPath = '';
      
      for (let i = 0; i < pathParts.length; i++) {
        accumulatedPath += (i > 0 ? '/' : '') + pathParts[i];
        crumbs.push({
          name: pathParts[i],
          path: accumulatedPath
        });
      }
      
      setBreadcrumbs(crumbs);
    } catch (err) {
      console.error('Failed to fetch files:', err);
      setError(err.message);
      setFiles([]);
    } finally {
      setIsLoading(false);
    }
  };

  const navigateToDirectory = (path) => {
    setCurrentPath(path);
  };

  const navigateUp = () => {
    if (!currentPath) return;
    
    const pathParts = currentPath.split('/');
    pathParts.pop();
    setCurrentPath(pathParts.join('/'));
  };

  const handleFileClick = (file) => {
    if (file.is_directory) {
      navigateToDirectory(file.path);
    } else {
      if (onFileSelect) {
        onFileSelect(file);
      }
    }
  };

  const handleDownload = async (file, e) => {
    e.stopPropagation();
    try {
      const blob = await apiService.downloadFile(file.path, (progress) => {
        // Update progress in UI if needed
        console.log(`Download progress: ${(progress * 100).toFixed(2)}%`);
      });
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err) {
      console.error('Download failed:', err);
      setError(err.message);
    }
  };

  if (error) {
    return (
      <div className="file-explorer error">
        <AlertCircle size={48} className="text-red-500 mb-4" />
        <h3 className="text-xl font-semibold mb-2">Error Loading Files</h3>
        <p className="text-gray-600 mb-4">{error}</p>
        <button 
          onClick={() => fetchFiles(currentPath)}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
        >
          Retry
        </button>
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
      <div className="file-explorer-header">
        <div className="flex items-center justify-between mb-2">
          <button
            onClick={navigateUp}
            disabled={!currentPath}
            className={`back-button ${!currentPath ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <ChevronLeft size={16} />
            Up
          </button>
          
          <div className="flex-1 ml-4">
            <div className="breadcrumbs flex items-center overflow-x-auto py-1">
              <button
                onClick={() => navigateToDirectory('')}
                className="text-blue-500 hover:text-blue-700 text-sm font-medium"
              >
                Root
              </button>
              
              {breadcrumbs.map((crumb, index) => (
                <React.Fragment key={index}>
                  <span className="mx-2 text-gray-400">/</span>
                  <button
                    onClick={() => navigateToDirectory(crumb.path)}
                    className="text-blue-500 hover:text-blue-700 text-sm font-medium whitespace-nowrap"
                  >
                    {crumb.name}
                  </button>
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
        
        <div className="path text-sm text-gray-500 truncate">
          {currentPath || 'Root directory'}
        </div>
      </div>
      
      {files.length === 0 ? (
        <div className="empty-directory">
          <Folder size={48} className="mx-auto mb-4 text-gray-400" />
          <h3 className="text-lg font-medium text-gray-600">Empty directory</h3>
          <p className="text-gray-500">No files found in this location</p>
        </div>
      ) : (
        <div className="file-grid">
          {files.map((file) => (
            <div
              key={file.path}
              onClick={() => handleFileClick(file)}
              className={`file-item ${file.is_directory ? 'directory' : ''}`}
            >
              <div className="file-icon">
                {file.is_directory ? (
                  <Folder size={24} />
                ) : (
                  <File size={24} />
                )}
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
                  className="download-button"
                  title="Download file"
                >
                  <Download size={16} />
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileExplorer;