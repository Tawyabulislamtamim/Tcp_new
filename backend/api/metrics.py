import threading
from dataclasses import dataclass
from typing import Dict, List, Optional
from collections import defaultdict, deque
from flask import Blueprint, request, jsonify, Response, current_app
import json
import time

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/global')
def get_global_metrics():
    metrics_collector = current_app.config['METRICS_COLLECTOR']
    return jsonify(metrics_collector.get_global_metrics())

@metrics_bp.route('/client/<client_id>')
def get_client_metrics(client_id):
    metrics_collector = current_app.config['METRICS_COLLECTOR']
    client_metrics = metrics_collector.get_client_metrics(client_id)
    
    return jsonify({
        'client_id': client_id,
        'metrics': [
            {
                'timestamp': m.timestamp,
                'cwnd': m.cwnd,
                'ssthresh': m.ssthresh,
                'rtt': m.rtt,
                'bandwidth': m.bandwidth,
                'packet_loss': m.packet_loss,
                'algorithm': m.algorithm
            }
            for m in client_metrics
        ]
    })

@metrics_bp.route('/stream')
def stream_metrics():
    def generate():
        metrics_collector = current_app.config['METRICS_COLLECTOR']
        
        while True:
            try:
                global_metrics = metrics_collector.get_global_metrics()
                yield f"data: {json.dumps(global_metrics)}\n\n"
                time.sleep(0.5)  # Update every 500ms
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
                
    return Response(generate(), mimetype='text/event-stream')

@metrics_bp.route('/history')
def get_metrics_history():
    metrics_collector = current_app.config['METRICS_COLLECTOR']
    seconds = request.args.get('seconds', 30, type=int)
    
    recent_metrics = metrics_collector.get_recent_metrics(seconds)
    
    return jsonify({
        'metrics': [
            {
                'timestamp': m.timestamp,
                'cwnd': m.cwnd,
                'ssthresh': m.ssthresh,
                'rtt': m.rtt,
                'bandwidth': m.bandwidth,
                'packet_loss': m.packet_loss,
                'algorithm': m.algorithm,
                'client_id': m.client_id
            }
            for m in recent_metrics
        ],
        'timespan': seconds
    })