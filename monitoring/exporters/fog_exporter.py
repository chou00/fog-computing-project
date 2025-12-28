"""
Prometheus Exporter for Fog Nodes
Exports fog node metrics to Prometheus
"""

from prometheus_client import start_http_server, Gauge, Counter, Histogram
from typing import Optional
from loguru import logger
import time


class FogNodeExporter:
    """Prometheus exporter for fog node metrics"""
    
    def __init__(self, node_id: str, port: int = 9090):
        """
        Initialize Prometheus exporter
        
        Args:
            node_id: Node identifier
            port: HTTP server port for metrics
        """
        self.node_id = node_id
        self.port = port
        
        # Define metrics
        self.cpu_usage = Gauge(
            'fog_node_cpu_usage_percent',
            'CPU usage percentage',
            ['node_id']
        )
        
        self.memory_usage = Gauge(
            'fog_node_memory_usage_percent',
            'Memory usage percentage',
            ['node_id']
        )
        
        self.network_in_bytes = Counter(
            'fog_node_network_in_bytes_total',
            'Total network input bytes',
            ['node_id']
        )
        
        self.network_out_bytes = Counter(
            'fog_node_network_out_bytes_total',
            'Total network output bytes',
            ['node_id']
        )
        
        self.active_connections = Gauge(
            'fog_node_active_connections',
            'Number of active connections',
            ['node_id']
        )
        
        self.packet_count = Counter(
            'fog_node_packets_total',
            'Total packet count',
            ['node_id', 'direction']
        )
        
        self.latency_histogram = Histogram(
            'fog_node_packet_latency_seconds',
            'Packet latency distribution',
            ['node_id'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0]
        )
        
        self.load_score = Gauge(
            'fog_node_load_score',
            'Composite load score (0-1)',
            ['node_id']
        )
        
        self.predicted_load = Gauge(
            'fog_node_predicted_load',
            'Predicted future load (0-1)',
            ['node_id']
        )
        
        self.anomaly_score = Gauge(
            'fog_node_anomaly_score',
            'Anomaly detection score (0-1)',
            ['node_id']
        )
        
        self.is_anomaly = Gauge(
            'fog_node_is_anomaly',
            'Whether anomaly is detected (0 or 1)',
            ['node_id']
        )
        
        logger.info(f"Fog Node Exporter initialized: node_id={node_id}, port={port}")
    
    def start(self):
        """Start the Prometheus HTTP server"""
        try:
            start_http_server(self.port)
            logger.info(f"Prometheus exporter started on port {self.port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus exporter: {e}")
    
    def update_metrics(self, metrics: dict):
        """
        Update metrics from node metrics
        
        Args:
            metrics: Dictionary with node metrics
        """
        labels = [self.node_id]
        
        # Update basic metrics
        if 'cpu_usage' in metrics:
            self.cpu_usage.labels(*labels).set(metrics['cpu_usage'])
        
        if 'memory_usage' in metrics:
            self.memory_usage.labels(*labels).set(metrics['memory_usage'])
        
        if 'network_in' in metrics:
            self.network_in_bytes.labels(*labels).inc(metrics['network_in'])
        
        if 'network_out' in metrics:
            self.network_out_bytes.labels(*labels).inc(metrics['network_out'])
        
        if 'active_connections' in metrics:
            self.active_connections.labels(*labels).set(metrics['active_connections'])
        
        if 'packet_count' in metrics:
            self.packet_count.labels(self.node_id, 'in').inc(metrics.get('packets_in', 0))
            self.packet_count.labels(self.node_id, 'out').inc(metrics.get('packets_out', 0))
        
        if 'latency' in metrics:
            self.latency_histogram.labels(*labels).observe(metrics['latency'] / 1000.0)  # Convert ms to seconds
        
        # Update AI-related metrics
        if 'load_score' in metrics:
            self.load_score.labels(*labels).set(metrics['load_score'])
        
        if 'predicted_load' in metrics:
            self.predicted_load.labels(*labels).set(metrics['predicted_load'])
        
        if 'anomaly_score' in metrics:
            self.anomaly_score.labels(*labels).set(metrics['anomaly_score'])
        
        if 'is_anomaly' in metrics:
            self.is_anomaly.labels(*labels).set(1 if metrics['is_anomaly'] else 0)

