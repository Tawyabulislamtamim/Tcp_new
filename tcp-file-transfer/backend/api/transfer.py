from flask import Blueprint, request, jsonify, current_app
from models.transfer_handler import TransferHandler

transfer_bp = Blueprint('transfer', __name__)

@transfer_bp.route('/download')
def download_file():
    """Endpoint to download a file"""
    file_path = request.args.get('path')
    client_id = request.args.get('client_id')
    
    if not file_path or not client_id:
        return jsonify({'error': 'Missing path or client_id'}), 400
    
    file_manager = current_app.config['FILE_MANAGER']
    transfer_handler = current_app.config['TRANSFER_HANDLER']
    
    file_path_obj = file_manager.get_file_path(file_path)
    if not file_path_obj:
        return jsonify({'error': 'File not found'}), 404
    
    file_info = file_manager.get_file_info(file_path)
    transfer_id = transfer_handler.start_transfer(
        client_id, 
        file_path_obj, 
        file_info.size
    )
    
    return jsonify({
        'transfer_id': transfer_id,
        'file_size': file_info.size
    })

@transfer_bp.route('/status/<transfer_id>')
def get_transfer_status(transfer_id):
    """Check status of a file transfer"""
    transfer_handler = current_app.config['TRANSFER_HANDLER']
    status = transfer_handler.get_transfer_progress(transfer_id)
    
    if not status:
        return jsonify({'error': 'Transfer not found'}), 404
        
    return jsonify(status)