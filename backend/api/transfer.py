from flask import Blueprint, request, jsonify, current_app, Response
import os
import time
import uuid
from pathlib import Path
import threading

transfer_bp = Blueprint('transfer', __name__)

# Store active downloads globally
active_downloads = {}
download_lock = threading.Lock()

class DownloadSession:
    def __init__(self, client_id, file_path, file_size):
        self.session_id = str(uuid.uuid4())
        self.client_id = client_id
        self.file_path = file_path
        self.file_size = file_size
        self.bytes_transferred = 0
        self.start_time = time.time()
        self.chunk_size = 64 * 1024  # 64KB chunks for smooth progress
        self.is_complete = False
        self.error = None
        self.is_processing = False
        self.is_streaming = False  # Track if currently streaming to browser
        
    def get_progress(self):
        elapsed = time.time() - self.start_time
        speed = self.bytes_transferred / elapsed if elapsed > 0 else 0
        eta = (self.file_size - self.bytes_transferred) / speed if speed > 0 else 0
        
        return {
            'session_id': self.session_id,
            'bytes_transferred': self.bytes_transferred,
            'total_size': self.file_size,
            'progress_percent': (self.bytes_transferred / self.file_size) * 100,
            'speed_bps': speed,
            'speed_mbps': speed / (1024 * 1024),
            'eta_seconds': eta,
            'elapsed_seconds': elapsed,
            'is_complete': self.is_complete,
            'is_processing': self.is_streaming,
            'is_ready_for_download': True,  # Always ready - we stream directly
            'error': self.error
        }

@transfer_bp.route('/start-download', methods=['POST'])
def start_download():
    """Start a tracked download session"""
    try:
        data = request.get_json()
        file_path = data.get('path')
        client_id = data.get('client_id')
        
        if not file_path or not client_id:
            return jsonify({'error': 'Missing path or client_id'}), 400
        
        # Get file manager and validate file
        file_manager = current_app.config['FILE_MANAGER']
        file_path_obj = file_manager.get_file_path(file_path)
        
        if not file_path_obj or not os.path.isfile(file_path_obj):
            return jsonify({'error': 'File not found'}), 404
        
        file_size = os.path.getsize(file_path_obj)
        
        # Create download session
        session = DownloadSession(client_id, file_path_obj, file_size)
        
        with download_lock:
            active_downloads[session.session_id] = session
        
        # Get or create TCP client for tracking
        connection_manager = current_app.config['CONNECTION_MANAGER']
        client = connection_manager.get_client(client_id)
        if not client:
            client_id = connection_manager.register_client(is_demo=False)
            client = connection_manager.get_client(client_id)
        
        current_app.logger.info(f"Started download session {session.session_id} for {os.path.basename(file_path_obj)} ({file_size} bytes)")
        
        # No background processing - we'll stream directly when requested
        
        return jsonify({
            'session_id': session.session_id,
            'file_name': os.path.basename(file_path_obj),
            'file_size': file_size,
            'client_id': client_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error starting download: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transfer_bp.route('/stream-download/<session_id>')
def stream_download(session_id):
    """Stream file with real-time metrics collection"""
    try:
        with download_lock:
            session = active_downloads.get(session_id)
        
        if not session:
            return jsonify({'error': 'Download session not found'}), 404
        
        if session.error:
            return jsonify({'error': session.error}), 500
        
        # Get components for metrics collection BEFORE creating the generator
        # This ensures we're in the Flask request context
        connection_manager = current_app.config['CONNECTION_MANAGER']
        metrics_collector = current_app.config['METRICS_COLLECTOR']
        client = connection_manager.get_client(session.client_id)
        
        def generate_with_metrics():
            """Stream file chunks while collecting TCP metrics"""
            try:
                session.is_streaming = True
                
                chunk_size = 32 * 1024  # 32KB chunks for good balance
                
                with open(session.file_path, 'rb') as f:
                    while True:
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        
                        # Update session progress
                        session.bytes_transferred += len(chunk)
                        
                        # Update TCP client metrics
                        if client:
                            client.transfer_stats['bytes_sent'] += len(chunk)
                            client.update_activity()
                            
                            # Simulate network activity for TCP metrics
                            rtt, bandwidth = client.simulate_network_activity()
                            
                            # Record metrics
                            from models.metrics_collector import NetworkMetrics
                            
                            metrics = NetworkMetrics(
                                timestamp=time.time(),
                                cwnd=client.tcp_controller.get_current_cwnd(),
                                ssthresh=client.tcp_controller.get_ssthresh(),
                                rtt=rtt,
                                bandwidth=bandwidth,
                                packet_loss=client.tcp_controller.get_packet_loss_rate(),
                                algorithm=client.tcp_controller.get_current_algorithm(),
                                client_id=session.client_id
                            )
                            
                            # Add transfer-specific metrics
                            if hasattr(metrics, '__dict__'):
                                metrics.__dict__.update({
                                    'is_demo': False,
                                    'transfer_session': session.session_id,
                                    'bytes_transferred': session.bytes_transferred,
                                    'transfer_progress': (session.bytes_transferred / session.file_size) * 100
                                })
                            
                            metrics_collector.record_metrics(session.client_id, metrics)
                        
                        # Yield chunk to browser
                        yield chunk
                        
                        # Small delay for realistic network simulation
                        time.sleep(0.001)  # 1ms delay per chunk
                
                # Mark as complete
                session.is_complete = True
                session.is_streaming = False
                
                # Use basic logging since we're outside Flask context
                import logging
                logging.info(f"Download completed for session {session_id} - {session.bytes_transferred} bytes")
            
            except Exception as e:
                session.error = str(e)
                session.is_streaming = False
                import logging
                logging.error(f"Error streaming file {session_id}: {str(e)}")
                raise
        
        # Return file as streaming response
        filename = os.path.basename(session.file_path)
        response = Response(
            generate_with_metrics(),
            mimetype='application/octet-stream',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"',
                'Content-Length': str(session.file_size),
                'Cache-Control': 'no-cache',
                'X-Session-ID': session_id  # For debugging
            }
        )
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error streaming download {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transfer_bp.route('/download-progress/<session_id>')
def get_download_progress(session_id):
    """Get real-time download progress"""
    try:
        with download_lock:
            session = active_downloads.get(session_id)
        
        if not session:
            return jsonify({'error': 'Download session not found'}), 404
        
        progress = session.get_progress()
        
        # Clean up completed sessions after some time
        if session.is_complete and time.time() - session.start_time > 300:  # 5 minutes
            with download_lock:
                if session_id in active_downloads:
                    del active_downloads[session_id]
        
        return jsonify(progress), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting download progress {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@transfer_bp.route('/cancel-download/<session_id>', methods=['POST'])
def cancel_download(session_id):
    """Cancel an active download"""
    try:
        with download_lock:
            session = active_downloads.get(session_id)
            if session:
                session.error = "Download cancelled by user"
                del active_downloads[session_id]
        
        current_app.logger.info(f"Download session {session_id} cancelled")
        return jsonify({'success': True}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling download {session_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Legacy download endpoint (keep for compatibility)
@transfer_bp.route('/download')
def download_file():
    """Legacy endpoint - redirect to tracked download"""
    file_path = request.args.get('path')
    client_id = request.args.get('client_id')
    
    if not file_path or not client_id:
        return jsonify({'error': 'Missing path or client_id'}), 400
    
    # This will be handled by the frontend to use the new streaming system
    return jsonify({
        'message': 'Use /start-download for tracked downloads',
        'path': file_path,
        'client_id': client_id
    }), 200

@transfer_bp.route('/status/<transfer_id>')
def get_transfer_status(transfer_id):
    """Check status of a file transfer (legacy)"""
    # Redirect to new progress endpoint
    return get_download_progress(transfer_id)