from flask import Blueprint, request, jsonify, current_app, send_file, abort
import os
import time
from werkzeug.utils import secure_filename
from pathlib import Path
import time

files_bp = Blueprint('files', __name__)

@files_bp.route('/config/demo-mode', methods=['GET', 'POST'])
def demo_mode_config():
    """Get or set demo mode configuration"""
    if request.method == 'GET':
        demo_mode = current_app.config.get('DEMO_MODE', False)
        return jsonify({
            'demo_mode': demo_mode,
            'description': 'Demo mode creates simulated connections for testing'
        })
    
    elif request.method == 'POST':
        data = request.get_json()
        if 'demo_mode' not in data:
            return jsonify({'error': 'demo_mode field required'}), 400
        
        demo_mode = bool(data['demo_mode'])
        current_app.config['DEMO_MODE'] = demo_mode
        
        # If demo mode is disabled, clean up demo clients
        if not demo_mode:
            connection_manager = current_app.config['CONNECTION_MANAGER']
            with connection_manager.lock:
                demo_clients = [cid for cid, client in connection_manager.clients.items() 
                              if getattr(client, 'is_demo', False)]
                for cid in demo_clients:
                    del connection_manager.clients[cid]
                    
                current_app.logger.info(f"Removed {len(demo_clients)} demo clients")
        
        return jsonify({
            'demo_mode': demo_mode,
            'message': f'Demo mode {"enabled" if demo_mode else "disabled"}'
        })

@files_bp.route('/list')
def list_files():
    path = request.args.get('path', '')
    file_manager = current_app.config['FILE_MANAGER']
    
    try:
        files = file_manager.list_directory(path)
        return jsonify({
            'files': [
                {
                    'name': f.name,
                    'path': f.path,
                    'size': f.size,
                    'is_directory': f.is_directory,
                    'modified_time': f.modified_time,
                    'mime_type': f.mime_type
                }
                for f in files
            ],
            'current_path': path
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@files_bp.route('/info')
def get_file_info():
    path = request.args.get('path', '')
    file_manager = current_app.config['FILE_MANAGER']
    
    file_info = file_manager.get_file_info(path)
    if not file_info:
        return jsonify({'error': 'File not found'}), 404
        
    return jsonify({
        'name': file_info.name,
        'path': file_info.path,
        'size': file_info.size,
        'is_directory': file_info.is_directory,
        'modified_time': file_info.modified_time,
        'mime_type': file_info.mime_type
    })

@files_bp.route('/download')
def direct_download():
    path = request.args.get('path')
    file_manager = current_app.config['FILE_MANAGER']
    
    try:
        file_path_obj = file_manager.get_file_path(path)

        if not file_path_obj:
            return jsonify({'error': 'File not resolved'}), 404

        if not os.path.isfile(file_path_obj):
            return jsonify({'error': 'Resolved path is not a file'}), 404

        return send_file(file_path_obj, as_attachment=True)

    except Exception as e:
        print("❌ Download error:", str(e))
        return jsonify({'error': str(e)}), 500

@files_bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file and create a real TCP connection for transfer"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Get current path for upload destination
        current_path = request.form.get('path', '')
        
        # Secure the filename
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400
        
        # Determine upload directory
        upload_dir = Path(current_app.config['UPLOAD_FOLDER'])
        if current_path:
            upload_dir = upload_dir / current_path
        
        upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = upload_dir / filename
        
        # Check if file already exists
        if file_path.exists():
            # Add timestamp to make filename unique
            timestamp = int(time.time())
            name, ext = os.path.splitext(filename)
            filename = f"{name}_{timestamp}{ext}"
            file_path = upload_dir / filename
        
        # Create a real TCP connection for this upload
        connection_manager = current_app.config['CONNECTION_MANAGER']
        client_id = connection_manager.register_client(is_demo=False)
        client = connection_manager.get_client(client_id)
        
        # Save the file (simulating TCP transfer)
        file.save(str(file_path))
        file_size = file_path.stat().st_size
        
        # Update client transfer stats
        if client:
            client.transfer_stats['bytes_received'] += file_size
            client.transfer_stats['active_transfers'] += 1
            
            # Simulate network conditions during upload
            client.simulate_network_activity()
            
            # Log successful upload with TCP metrics
            tcp_controller = client.tcp_controller
            current_app.logger.info(
                f"File uploaded via REAL client {client_id}: {filename} "
                f"({file_size} bytes, algorithm: {tcp_controller.get_current_algorithm()})"
            )
        
        return jsonify({
            'success': True,
            'filename': filename,
            'size': file_size,
            'path': str(file_path.relative_to(current_app.config['UPLOAD_FOLDER'])),
            'client_id': client_id,
            'algorithm': client.tcp_controller.get_current_algorithm() if client else 'unknown'
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Upload error: {str(e)}")
        return jsonify({'error': str(e)}), 500
    
  