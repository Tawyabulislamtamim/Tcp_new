from flask import Blueprint, request, jsonify, current_app

files_bp = Blueprint('files', __name__)

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
    
    from flask import send_file, abort
import os

@files_bp.route('/download')
def direct_download():
    from flask import send_file, abort
    import os

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

