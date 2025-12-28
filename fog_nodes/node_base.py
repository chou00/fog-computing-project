"""
Base Fog Node Implementation
Provides common functionality for all fog nodes
"""

import time
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from loguru import logger


@dataclass
class NodeMetrics:
    """Metrics collected from a fog node"""
    node_id: str
    timestamp: float
    cpu_usage: float  # Percentage
    memory_usage: float  # Percentage
    network_in: float  # Bytes/sec
    network_out: float  # Bytes/sec
    active_connections: int
    packet_count: int
    latency: float  # ms


class FogNodeBase:
    """Base class for fog nodes"""
    
    def __init__(self, node_id: str, architecture: str = 'distributed_ai'):
        """
        Initialize fog node
        
        Args:
            node_id: Unique identifier for the node
            architecture: Architecture type ('centralized', 'distributed_no_ai', 'distributed_ai')
        """
        self.node_id = node_id
        self.architecture = architecture
        self.metrics_history: List[NodeMetrics] = []
        self.neighbors: List[str] = []
        self.is_running = False
        self.monitoring_thread: Optional[threading.Thread] = None
        self.metrics_lock = threading.Lock()
        
        logger.info(f"Fog node {node_id} initialized with architecture {architecture}")
    
    def start(self):
        """Start the fog node"""
        if self.is_running:
            logger.warning(f"Node {self.node_id} is already running")
            return
        
        self.is_running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info(f"Fog node {self.node_id} started")
    
    def stop(self):
        """Stop the fog node"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info(f"Fog node {self.node_id} stopped")
    
    def _monitoring_loop(self):
        """Internal monitoring loop"""
        while self.is_running:
            try:
                metrics = self._collect_metrics()
                with self.metrics_lock:
                    self.metrics_history.append(metrics)
                    # Keep only last 1000 metrics
                    if len(self.metrics_history) > 1000:
                        self.metrics_history.pop(0)
                
                time.sleep(1)  # Collect metrics every second
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(1)
    
    def _collect_metrics(self) -> NodeMetrics:
        """
        Collect current node metrics
        Override in subclasses for actual implementation
        """
        # Placeholder implementation
        return NodeMetrics(
            node_id=self.node_id,
            timestamp=time.time(),
            cpu_usage=0.0,
            memory_usage=0.0,
            network_in=0.0,
            network_out=0.0,
            active_connections=0,
            packet_count=0,
            latency=0.0
        )
    
    def get_current_metrics(self) -> Optional[NodeMetrics]:
        """Get the most recent metrics"""
        with self.metrics_lock:
            if self.metrics_history:
                return self.metrics_history[-1]
        return None
    
    def get_metrics_history(self, window_seconds: int = 60) -> List[NodeMetrics]:
        """
        Get metrics history for a time window
        
        Args:
            window_seconds: Time window in seconds
        """
        current_time = time.time()
        with self.metrics_lock:
            return [
                m for m in self.metrics_history
                if current_time - m.timestamp <= window_seconds
            ]
    
    def add_neighbor(self, neighbor_id: str):
        """Add a neighbor node"""
        if neighbor_id not in self.neighbors:
            self.neighbors.append(neighbor_id)
            logger.info(f"Added neighbor {neighbor_id} to node {self.node_id}")
    
    def remove_neighbor(self, neighbor_id: str):
        """Remove a neighbor node"""
        if neighbor_id in self.neighbors:
            self.neighbors.remove(neighbor_id)
            logger.info(f"Removed neighbor {neighbor_id} from node {self.node_id}")
    
    def get_neighbors(self) -> List[str]:
        """Get list of neighbor nodes"""
        return self.neighbors.copy()
    
    def route_packet(self, packet_info: Dict) -> Optional[str]:
        """
        Route a packet to the next hop
        Override in subclasses based on architecture
        
        Args:
            packet_info: Packet information (source, destination, type, etc.)
        
        Returns:
            Next hop node ID or None if destination reached
        """
        raise NotImplementedError("Subclasses must implement route_packet")
    
    def process_packet(self, packet_info: Dict):
        """
        Process an incoming packet
        Override in subclasses for specific processing
        
        Args:
            packet_info: Packet information
        """
        logger.debug(f"Node {self.node_id} processing packet: {packet_info}")

