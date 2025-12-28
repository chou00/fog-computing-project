"""
Load Monitoring Module for Fog Nodes
Collects real-time metrics: CPU, memory, network, connections
"""

import psutil
import time
from typing import Dict, List
from loguru import logger
from .node_base import NodeMetrics, FogNodeBase


class LoadMonitor:
    """Monitors system load and network metrics"""
    
    def __init__(self, node_id: str):
        """
        Initialize load monitor
        
        Args:
            node_id: Node identifier
        """
        self.node_id = node_id
        self.last_network_stats = psutil.net_io_counters()
        self.last_network_time = time.time()
        logger.info(f"Load monitor initialized for node {node_id}")
    
    def collect_metrics(self) -> NodeMetrics:
        """
        Collect current system metrics
        
        Returns:
            NodeMetrics object with current measurements
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Network statistics
            current_time = time.time()
            current_network_stats = psutil.net_io_counters()
            time_delta = current_time - self.last_network_time
            
            if time_delta > 0:
                network_in = (current_network_stats.bytes_recv - 
                             self.last_network_stats.bytes_recv) / time_delta
                network_out = (current_network_stats.bytes_sent - 
                              self.last_network_stats.bytes_sent) / time_delta
            else:
                network_in = 0.0
                network_out = 0.0
            
            self.last_network_stats = current_network_stats
            self.last_network_time = current_time
            
            # Active network connections
            connections = len(psutil.net_connections(kind='inet'))
            
            # Create metrics object
            metrics = NodeMetrics(
                node_id=self.node_id,
                timestamp=time.time(),
                cpu_usage=cpu_percent,
                memory_usage=memory_percent,
                network_in=network_in,
                network_out=network_out,
                active_connections=connections,
                packet_count=current_network_stats.packets_recv + current_network_stats.packets_sent,
                latency=0.0  # Will be measured separately
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            # Return default metrics on error
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
    
    def get_load_vector(self, metrics: NodeMetrics) -> List[float]:
        """
        Convert metrics to a feature vector for ML models
        
        Args:
            metrics: NodeMetrics object
        
        Returns:
            Feature vector [cpu, memory, network_in, network_out, connections]
        """
        return [
            metrics.cpu_usage / 100.0,  # Normalize to [0, 1]
            metrics.memory_usage / 100.0,
            min(metrics.network_in / 1e6, 1.0),  # Normalize to Mbps, cap at 1.0
            min(metrics.network_out / 1e6, 1.0),
            min(metrics.active_connections / 100.0, 1.0)  # Cap at 100 connections
        ]
    
    def calculate_load_score(self, metrics: NodeMetrics) -> float:
        """
        Calculate a composite load score (0-1, higher = more loaded)
        
        Args:
            metrics: NodeMetrics object
        
        Returns:
            Load score between 0 and 1
        """
        # Weighted combination of metrics
        cpu_weight = 0.3
        memory_weight = 0.3
        network_weight = 0.2
        connection_weight = 0.2
        
        cpu_score = metrics.cpu_usage / 100.0
        memory_score = metrics.memory_usage / 100.0
        network_score = min((metrics.network_in + metrics.network_out) / 2e6, 1.0)
        connection_score = min(metrics.active_connections / 100.0, 1.0)
        
        load_score = (
            cpu_weight * cpu_score +
            memory_weight * memory_score +
            network_weight * network_score +
            connection_weight * connection_score
        )
        
        return min(load_score, 1.0)

