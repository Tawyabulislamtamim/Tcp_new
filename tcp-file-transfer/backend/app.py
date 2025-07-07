from flask import Flask, request, jsonify
from flask_cors import CORS
import time

from models.file_manager import FileManager
from models.connection_manager import ConnectionManager
from models.metrics_collector import MetricsCollector
from models.transfer_handler import TransferHandler

from api.files import files_bp
from api.metrics import metrics_bp
from api.transfer import transfer_bp

app = Flask(__name__)
CORS(app)

# Initialize core components
metrics_collector = MetricsCollector()
connection_manager = ConnectionManager(metrics_collector)
file_manager = FileManager()
transfer_handler = TransferHandler(connection_manager)

# Make components available to blueprints
app.config['METRICS_COLLECTOR'] = metrics_collector
app.config['CONNECTION_MANAGER'] = connection_manager
app.config['FILE_MANAGER'] = file_manager
app.config['TRANSFER_HANDLER'] = transfer_handler

# Register blueprints
app.register_blueprint(files_bp, url_prefix='/api/files')
app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
app.register_blueprint(transfer_bp, url_prefix='/api/transfer')

# ✅ Health check route
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

@app.route('/api/connect', methods=['POST'])
def connect_client():
    client_id = connection_manager.register_client()
    return jsonify({'client_id': client_id})

@app.route('/api/disconnect', methods=['POST'])
def disconnect_client():
    client_id = request.json.get('client_id')
    if client_id:
        connection_manager.remove_client(client_id)
    return jsonify({'success': True})

@app.route('/api/status')
def get_status():
    return jsonify({
        'active_clients': len(connection_manager.get_active_clients()),
        'server_time': time.time(),
        'status': 'running'
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
