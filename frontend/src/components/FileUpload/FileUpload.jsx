import React, { useState, useRef } from 'react';
import './FileUpload.css';

const FileUpload = ({ currentPath, onUploadSuccess, onUploadError }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        
        const files = Array.from(e.dataTransfer.files);
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileSelect = (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            handleFileUpload(files[0]);
        }
    };

    const handleFileUpload = async (file) => {
        if (!file) return;

        setIsUploading(true);
        setUploadProgress(0);

        const formData = new FormData();
        formData.append('file', file);
        if (currentPath) {
            formData.append('path', currentPath);
        }

        try {
            const xhr = new XMLHttpRequest();

            // Track upload progress
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const progress = (e.loaded / e.total) * 100;
                    setUploadProgress(progress);
                }
            });

            // Handle completion
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    onUploadSuccess && onUploadSuccess(response);
                    setUploadProgress(100);
                    setTimeout(() => {
                        setIsUploading(false);
                        setUploadProgress(0);
                    }, 1000);
                } else {
                    const error = JSON.parse(xhr.responseText);
                    onUploadError && onUploadError(error.error || 'Upload failed');
                    setIsUploading(false);
                }
            });

            // Handle errors
            xhr.addEventListener('error', () => {
                onUploadError && onUploadError('Network error during upload');
                setIsUploading(false);
            });

            // Start upload
            xhr.open('POST', '/api/files/upload');
            
            xhr.send(formData);

        } catch (error) {
            onUploadError && onUploadError(error.message);
            setIsUploading(false);
        }
    };

    const openFileDialog = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="file-upload-container">
            <div
                className={`file-upload-area ${isDragging ? 'dragging' : ''} ${isUploading ? 'uploading' : ''}`}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={openFileDialog}
            >
                <input
                    ref={fileInputRef}
                    type="file"
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                    accept="*/*"
                />

                {isUploading ? (
                    <div className="upload-progress">
                        <div className="upload-icon">📤</div>
                        <h3>Uploading...</h3>
                        <div className="progress-bar">
                            <div 
                                className="progress-fill" 
                                style={{ width: `${uploadProgress}%` }}
                            ></div>
                        </div>
                        <p>{Math.round(uploadProgress)}% complete</p>
                    </div>
                ) : (
                    <div className="upload-prompt">
                        <div className="upload-icon">📁</div>
                        <h3>Upload Files</h3>
                        <p>Drag and drop files here or click to browse</p>
                        <button className="upload-button">Choose Files</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default FileUpload;
