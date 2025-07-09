from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import time
import logging
from logging.handlers import RotatingFileHandler
from threading import Thread
from datetime import datetime
from pathlib import Path
from config import Config

from models.file_manager import FileManager
from models.connection_manager import ConnectionManager
from models.metrics_collector import MetricsCollector
from models.transfer_handler import TransferHandler

from api.files import files_bp
from api.metrics import metrics_bp
from api.transfer import transfer_bp

def configure_logging(app):
    """Configure application logging"""
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, static_folder='../frontend/build', static_url_path='/static')

    # Initialize configuration
    Config.init_app(app)

    # Enhanced CORS configuration using configured origins
    CORS(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True,
            "max_age": 86400
        }
    })

    # Initialize logging
    configure_logging(app)

    # Initialize core components
    metrics_collector = MetricsCollector()
    connection_manager = ConnectionManager(metrics_collector)
    file_manager = FileManager()
    transfer_handler = TransferHandler(connection_manager)

    # Store components in app config
    app.config.update(
        METRICS_COLLECTOR=metrics_collector,
        CONNECTION_MANAGER=connection_manager,
        FILE_MANAGER=file_manager,
        TRANSFER_HANDLER=transfer_handler,
        SECRET_KEY=app.config.get('SECRET_KEY', 'dev-key-please-change')
    )

    # Register blueprints with URL prefixes
    app.register_blueprint(files_bp, url_prefix='/api/files')
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
    app.register_blueprint(transfer_bp, url_prefix='/api/transfer')

    # Serve frontend (React) SPA
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        static_path = Path(app.static_folder)
        requested_path = static_path / path

        if path != "" and requested_path.exists() and requested_path.is_file():
            return send_from_directory(static_path, path)
        else:
            return send_from_directory(static_path, 'index.html')

    # Register core routes and error handlers
    register_core_routes(app)
    register_error_handlers(app)

    # Start background tasks
    start_background_tasks(app)

    return app

def start_background_tasks(app):
    """Start any background tasks needed by the application"""
    def cleanup_task():
        """Regularly clean up inactive resources"""
        with app.app_context():
            while True:
                try:
                    cm = app.config['CONNECTION_MANAGER']
                    inactive_count = cm.cleanup_inactive_clients()
                    if inactive_count > 0:
                        app.logger.info(f"Cleaned up {inactive_count} inactive clients")
                    time.sleep(app.config.get('CLEANUP_INTERVAL', 60))
                except Exception as e:
                    app.logger.error(f"Cleanup task error: {str(e)}")
                    time.sleep(10)

    def generate_sample_metrics():
        """Generate sample metrics data with adaptive algorithm switching"""
        import random
        from models.metrics_collector import NetworkMetrics
        
        with app.app_context():
            while True:
                try:
                    time.sleep(2)  # Generate metrics every 2 seconds
                    
                    metrics_collector = app.config['METRICS_COLLECTOR']
                    connection_manager = app.config['CONNECTION_MANAGER']
                    
                    # Create sample clients if none exist (simulate multiple algorithms)
                    active_clients = connection_manager.get_active_clients()
                    if len(active_clients) < 3:  # Maintain 3 active clients for demonstration
                        for i in range(3 - len(active_clients)):
                            sample_client_id = connection_manager.register_client()
                            client = connection_manager.get_client(sample_client_id)
                            if client:
                                # Start with different algorithms
                                algorithms = ['reno', 'cubic', 'tahoe', 'bbr']
                                algorithm = algorithms[i % len(algorithms)]
                                app.logger.info(f"Created client {sample_client_id} with {algorithm} algorithm")
                    
                    # Generate metrics for all active clients with adaptive switching
                    for client_id, client in connection_manager.get_active_clients().items():
                        # Simulate network activity and get conditions
                        rtt, bandwidth = client.simulate_network_activity()
                        
                        # Get current TCP controller state
                        tcp_controller = client.tcp_controller
                        performance_metrics = tcp_controller.get_performance_metrics()
                        
                        # Create comprehensive metrics
                        metrics = NetworkMetrics(
                            timestamp=time.time(),
                            cwnd=tcp_controller.get_current_cwnd(),
                            ssthresh=tcp_controller.get_ssthresh(),
                            rtt=rtt,
                            bandwidth=bandwidth,
                            packet_loss=tcp_controller.get_packet_loss_rate(),
                            algorithm=tcp_controller.get_current_algorithm(),
                            client_id=client_id
                        )
                        
                        # Add additional algorithm-specific metrics
                        if hasattr(metrics, '__dict__'):
                            metrics.__dict__.update({
                                'algorithm_state': performance_metrics['algorithm_state'],
                                'network_condition': performance_metrics['network_condition'],
                                'packets_sent': performance_metrics['packets_sent'],
                                'packets_lost': performance_metrics['packets_lost'],
                                'time_since_switch': performance_metrics['switch_history']['time_since_switch']
                            })
                        
                        metrics_collector.record_metrics(client_id, metrics)
                        
                        # Log algorithm switches
                        if performance_metrics['switch_history']['time_since_switch'] < 3.0:
                            app.logger.info(f"Client {client_id}: Algorithm switched to {performance_metrics['current_algorithm']} "
                                          f"(Condition: {performance_metrics['network_condition']}, "
                                          f"State: {performance_metrics['algorithm_state']})")
                        
                except Exception as e:
                    app.logger.error(f"Error generating adaptive metrics: {str(e)}")
                    time.sleep(5)
                        
                except Exception as e:
                    app.logger.error(f"Error generating sample metrics: {str(e)}")
                    time.sleep(5)

    cleanup_thread = Thread(target=cleanup_task, daemon=True)
    cleanup_thread.start()
    
    metrics_thread = Thread(target=generate_sample_metrics, daemon=True)
    metrics_thread.start()
    
    app.logger.info("Background tasks started: cleanup and metrics generation")

def register_error_handlers(app):
    """Register custom error handlers"""
    @app.errorhandler(400)
    def bad_request(error):
        app.logger.warning(f"Bad request: {str(error)}")
        return jsonify({
            'error': 'Bad request',
            'message': str(error),
            'status_code': 400,
            'timestamp': datetime.utcnow().isoformat()
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        app.logger.info(f"Not found: {str(error)}")
        return jsonify({
            'error': 'Not found',
            'message': str(error),
            'status_code': 404,
            'timestamp': datetime.utcnow().isoformat()
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server error: {str(error)}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred',
            'status_code': 500,
            'timestamp': datetime.utcnow().isoformat()
        }), 500

def register_core_routes(app):
    """Register core application routes"""
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {
                'connection_manager': True,
                'file_manager': True,
                'metrics_collector': True,
                'transfer_handler': True
            },
            'endpoints': {
                'files': '/api/files',
                'metrics': '/api/metrics',
                'transfer': '/api/transfer'
            }
        }), 200

    @app.route('/api/connect', methods=['POST'])
    def connect_client():
        try:
            cm = app.config['CONNECTION_MANAGER']
            client_id = cm.register_client()
            app.logger.info(f"New client connected: {client_id}")
            return jsonify({
                'client_id': client_id,
                'status': 'connected',
                'timestamp': datetime.utcnow().isoformat(),
                'algorithm': app.config.get('DEFAULT_ALGORITHM', 'reno')
            }), 201
        except Exception as e:
            app.logger.error(f"Connection error: {str(e)}")
            return jsonify({
                'error': 'Connection failed',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/disconnect', methods=['POST'])
    def disconnect_client():
        client_id = request.json.get('client_id')
        if not client_id:
            return jsonify({
                'error': 'Missing client_id',
                'status_code': 400,
                'timestamp': datetime.utcnow().isoformat()
            }), 400
        try:
            cm = app.config['CONNECTION_MANAGER']
            cm.remove_client(client_id)
            app.logger.info(f"Client disconnected: {client_id}")
            return jsonify({
                'success': True,
                'client_id': client_id,
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            app.logger.error(f"Disconnection error: {str(e)}")
            return jsonify({
                'error': 'Disconnection failed',
                'message': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }), 500

    @app.route('/api/status')
    def get_status():
        cm = app.config['CONNECTION_MANAGER']
        th = app.config['TRANSFER_HANDLER']
        active_clients = cm.get_active_clients()

        return jsonify({
            'status': 'running',
            'server_time': datetime.utcnow().isoformat(),
            'uptime': round(time.time() - app.start_time, 2),
            'active_clients': len(active_clients),
            'metrics': {
                'total_transfers': getattr(th, 'total_transfers', 0),
                'active_transfers': len(getattr(th, 'active_transfers', {}))
            },
            'config': {
                'default_algorithm': app.config.get('DEFAULT_ALGORITHM', 'reno'),
                'chunk_size': app.config.get('CHUNK_SIZE', 8192)
            }
        })

# Application initialization
app = create_app()
app.start_time = time.time()

if __name__ == '__main__':
    app.logger.info("Starting TCP File Transfer Server")
    try:
        app.run(
            host=app.config.get('HOST', '0.0.0.0'),
            port=app.config.get('PORT', 5000),
            debug=app.config.get('DEBUG', False),
            threaded=True,
            use_reloader=False
        )
    except Exception as e:
        app.logger.critical(f"Failed to start server: {str(e)}")
        raise
