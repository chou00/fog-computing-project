"""
Complete Fog Node Implementation
Integrates all components: load monitoring, AI models, gRPC, MQTT
"""

import time
import threading
from typing import Dict, List, Optional
from loguru import logger
import sys
import os

# Add parent directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from fog_nodes.node_base import FogNodeBase, NodeMetrics
from fog_nodes.load_monitor import LoadMonitor
from fog_nodes.grpc_service import FogNodeService, FogNodeClient
from ai_models.lstm.model import LoadPredictor
from ai_models.autoencoder.model import AnomalyDetectionModel
from ai_models.rl.dqn_agent import DQNAgent
from monitoring.exporters.fog_exporter import FogNodeExporter


class FogNode(FogNodeBase):
    """Complete fog node with all AI components"""
    
    def __init__(self, node_id: str, architecture: str = 'distributed_ai',
                 grpc_port: int = 50051, prometheus_port: int = 9090):
        """
        Initialize complete fog node
        
        Args:
            node_id: Unique node identifier
            architecture: Architecture type
            grpc_port: gRPC server port
            prometheus_port: Prometheus exporter port
        """
        super().__init__(node_id, architecture)
        
        # Load monitoring
        self.load_monitor = LoadMonitor(node_id)
        
        # AI components (only for distributed_ai architecture)
        if architecture == 'distributed_ai':
            self.load_predictor = LoadPredictor(
                input_size=5,
                hidden_size=64,
                num_layers=2,
                sequence_length=60
            )
            
            self.anomaly_detector = AnomalyDetectionModel(
                input_size=10,
                encoding_dim=5,
                anomaly_threshold=0.1
            )
            
            self.rl_agent = DQNAgent(
                state_size=25,
                action_size=5,
                learning_rate=0.001,
                gamma=0.95
            )
        else:
            self.load_predictor = None
            self.anomaly_detector = None
            self.rl_agent = None
        
        # gRPC service
        self.grpc_service = FogNodeService(node_id, grpc_port)
        
        # Prometheus exporter
        self.exporter = FogNodeExporter(node_id, prometheus_port)
        
        # State
        self.predicted_load = 0.5
        self.anomaly_score = 0.0
        self.is_anomaly = False
        
        logger.info(f"Fog Node {node_id} initialized with architecture {architecture}")
    
    def start(self):
        """Start the fog node"""
        super().start()
        
        # Start gRPC server
        self.grpc_service.start_server()
        
        # Start Prometheus exporter
        self.exporter.start()
        
        logger.info(f"Fog Node {self.node_id} started")
    
    def stop(self):
        """Stop the fog node"""
        super().stop()
        self.grpc_service.stop_server()
        logger.info(f"Fog Node {self.node_id} stopped")
    
    def _collect_metrics(self) -> NodeMetrics:
        """Collect current node metrics"""
        return self.load_monitor.collect_metrics()
    
    def update_ai_models(self):
        """Update AI models with recent metrics"""
        if self.architecture != 'distributed_ai':
            return
        
        metrics_history = self.get_metrics_history(window_seconds=300)
        
        if len(metrics_history) < 60:
            return
        
        try:
            # Update load prediction
            self.predicted_load = self.load_predictor.predict_next_load(metrics_history)
            
            # Update anomaly detection
            features = self.anomaly_detector.extract_features(metrics_history)
            self.is_anomaly, self.anomaly_score = self.anomaly_detector.detect_anomaly(features)
            
            # Periodically retrain models
            if len(metrics_history) > 200 and len(metrics_history) % 100 == 0:
                logger.info("Retraining AI models...")
                self.load_predictor.train(metrics_history, epochs=5)
                
                # Train anomaly detector on normal traffic
                normal_features = [
                    self.anomaly_detector.extract_features(metrics_history[i:i+10])
                    for i in range(0, len(metrics_history)-10, 10)
                ]
                if normal_features:
                    self.anomaly_detector.train(normal_features, epochs=10)
        
        except Exception as e:
            logger.error(f"Error updating AI models: {e}")
    
    def route_packet(self, packet_info: Dict) -> Optional[str]:
        """
        Route a packet using appropriate method based on architecture
        
        Args:
            packet_info: Packet information
        
        Returns:
            Next hop node ID or None
        """
        if self.architecture == 'centralized':
            # Centralized: simple routing (handled by controller)
            return None
        
        elif self.architecture == 'distributed_no_ai':
            # Distributed without AI: rule-based load balancing
            neighbors = self.get_neighbors()
            if not neighbors:
                return None
            
            # Select least-loaded neighbor
            least_loaded = None
            min_load = float('inf')
            
            for neighbor_id in neighbors:
                neighbor_state = self.grpc_service.get_neighbor_state(neighbor_id)
                if neighbor_state:
                    load = neighbor_state.get('load', 0.5)
                    if load < min_load:
                        min_load = load
                        least_loaded = neighbor_id
            
            return least_loaded if least_loaded else neighbors[0]
        
        elif self.architecture == 'distributed_ai':
            # Distributed with AI: use RL agent
            if not self.rl_agent:
                return None
            
            current_metrics = self.get_current_metrics()
            neighbors = self.get_neighbors()
            
            # Build neighbor states
            neighbor_states = []
            for neighbor_id in neighbors[:5]:
                neighbor_state = self.grpc_service.get_neighbor_state(neighbor_id)
                if neighbor_state:
                    neighbor_states.append({
                        'load': neighbor_state.get('load', 0.5),
                        'latency': neighbor_state.get('latency', 5.0),
                        'anomaly_score': neighbor_state.get('anomaly_score', 0.0)
                    })
                else:
                    neighbor_states.append({
                        'load': 0.5,
                        'latency': 5.0,
                        'anomaly_score': 0.0
                    })
            
            # Build state for RL agent
            state = self.rl_agent.build_state(
                current_metrics,
                self.predicted_load,
                neighbor_states,
                self.anomaly_score
            )
            
            # Get action
            action = self.rl_agent.act(state, training=True)
            
            # Map action to neighbor
            if action < len(neighbors):
                return neighbors[action]
            elif neighbors:
                return neighbors[0]
        
        return None
    
    def _monitoring_loop(self):
        """Enhanced monitoring loop with AI updates and metrics export"""
        while self.is_running:
            try:
                # Collect metrics
                metrics = self._collect_metrics()
                with self.metrics_lock:
                    self.metrics_history.append(metrics)
                    if len(self.metrics_history) > 1000:
                        self.metrics_history.pop(0)
                
                # Update gRPC service state
                self.grpc_service.update_state({
                    'load': self.load_monitor.calculate_load_score(metrics),
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'network_usage': (metrics.network_in + metrics.network_out) / 1e6,
                    'anomaly_score': self.anomaly_score
                })
                
                # Update AI models periodically
                if self.architecture == 'distributed_ai' and len(self.metrics_history) % 10 == 0:
                    self.update_ai_models()
                
                # Export metrics to Prometheus
                self.exporter.update_metrics({
                    'cpu_usage': metrics.cpu_usage,
                    'memory_usage': metrics.memory_usage,
                    'network_in': metrics.network_in,
                    'network_out': metrics.network_out,
                    'active_connections': metrics.active_connections,
                    'latency': metrics.latency,
                    'load_score': self.load_monitor.calculate_load_score(metrics),
                    'predicted_load': self.predicted_load,
                    'anomaly_score': self.anomaly_score,
                    'is_anomaly': self.is_anomaly
                })
                
                time.sleep(1)  # Collect metrics every second
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)


if __name__ == '__main__':
    # Example usage
    import argparse
    
    parser = argparse.ArgumentParser(description='Fog Node')
    parser.add_argument('--node-id', type=str, required=True, help='Node ID')
    parser.add_argument('--architecture', type=str, default='distributed_ai',
                       choices=['centralized', 'distributed_no_ai', 'distributed_ai'],
                       help='Architecture type')
    parser.add_argument('--grpc-port', type=int, default=50051, help='gRPC port')
    parser.add_argument('--prometheus-port', type=int, default=9090, help='Prometheus port')
    
    args = parser.parse_args()
    
    # Create and start fog node
    node = FogNode(
        node_id=args.node_id,
        architecture=args.architecture,
        grpc_port=args.grpc_port,
        prometheus_port=args.prometheus_port
    )
    
    node.start()
    
    try:
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping fog node...")
        node.stop()

