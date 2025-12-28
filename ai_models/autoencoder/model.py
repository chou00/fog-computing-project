"""
Autoencoder Model for Network Anomaly Detection
Detects anomalies in network traffic patterns
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple
from loguru import logger


class AnomalyDetector(nn.Module):
    """Autoencoder for anomaly detection"""
    
    def __init__(self, input_size: int = 10, encoding_dim: int = 5, 
                 hidden_dims: List[int] = [64, 32]):
        """
        Initialize autoencoder
        
        Args:
            input_size: Number of input features
            encoding_dim: Dimension of encoding (bottleneck)
            hidden_dims: List of hidden layer dimensions
        """
        super(AnomalyDetector, self).__init__()
        
        self.input_size = input_size
        self.encoding_dim = encoding_dim
        
        # Encoder
        encoder_layers = []
        prev_dim = input_size
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        encoder_layers.append(nn.Linear(prev_dim, encoding_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Decoder
        decoder_layers = []
        prev_dim = encoding_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.append(nn.Linear(prev_dim, input_size))
        decoder_layers.append(nn.Sigmoid())  # Output in [0, 1]
        self.decoder = nn.Sequential(*decoder_layers)
        
        logger.info(f"Anomaly Detector initialized: input_size={input_size}, "
                   f"encoding_dim={encoding_dim}")
    
    def encode(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation"""
        return self.encoder(x)
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode latent representation to output"""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, input_size)
        
        Returns:
            Tuple of (reconstructed, encoded)
        """
        encoded = self.encode(x)
        reconstructed = self.decode(encoded)
        return reconstructed, encoded
    
    def reconstruction_error(self, x: torch.Tensor) -> torch.Tensor:
        """
        Calculate reconstruction error
        
        Args:
            x: Input tensor
        
        Returns:
            Reconstruction error (MSE)
        """
        reconstructed, _ = self.forward(x)
        error = nn.functional.mse_loss(reconstructed, x, reduction='none')
        return error.mean(dim=1)  # Mean error per sample


class AnomalyDetectionModel:
    """Wrapper class for anomaly detection with training and inference"""
    
    def __init__(self, input_size: int = 10, encoding_dim: int = 5, 
                 learning_rate: float = 0.001, anomaly_threshold: float = 0.1):
        """
        Initialize anomaly detection model
        
        Args:
            input_size: Number of input features
            encoding_dim: Encoding dimension
            learning_rate: Learning rate
            anomaly_threshold: Threshold for anomaly detection (reconstruction error)
        """
        self.input_size = input_size
        self.anomaly_threshold = anomaly_threshold
        
        # Initialize model
        self.model = AnomalyDetector(
            input_size=input_size,
            encoding_dim=encoding_dim
        )
        
        # Optimizer and loss
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        # Statistics for threshold adaptation
        self.reconstruction_errors = []
        
        logger.info(f"Anomaly Detection Model initialized with threshold={anomaly_threshold}")
    
    def extract_features(self, metrics_history: List, window_size: int = 10) -> np.ndarray:
        """
        Extract features from metrics history for anomaly detection
        
        Args:
            metrics_history: List of NodeMetrics objects
            window_size: Number of recent metrics to use
        
        Returns:
            Feature vector
        """
        if len(metrics_history) == 0:
            return np.zeros(self.input_size)
        
        # Use most recent metrics
        recent_metrics = metrics_history[-window_size:] if len(metrics_history) >= window_size else metrics_history
        
        features = []
        
        # Statistical features from recent window
        cpu_values = [m.cpu_usage for m in recent_metrics]
        memory_values = [m.memory_usage for m in recent_metrics]
        network_in_values = [m.network_in for m in recent_metrics]
        network_out_values = [m.network_out for m in recent_metrics]
        connection_values = [m.active_connections for m in recent_metrics]
        
        # Mean and std for each metric
        for values in [cpu_values, memory_values, network_in_values, network_out_values, connection_values]:
            if len(values) > 0:
                mean_val = np.mean(values)
                std_val = np.std(values) if len(values) > 1 else 0.0
                features.extend([mean_val / 100.0, std_val / 100.0])  # Normalize
            else:
                features.extend([0.0, 0.0])
        
        # Pad or truncate to input_size
        if len(features) < self.input_size:
            features.extend([0.0] * (self.input_size - len(features)))
        elif len(features) > self.input_size:
            features = features[:self.input_size]
        
        return np.array(features)
    
    def train(self, normal_traffic_data: List, epochs: int = 20, batch_size: int = 32):
        """
        Train on normal traffic data
        
        Args:
            normal_traffic_data: List of feature vectors from normal traffic
            epochs: Number of training epochs
            batch_size: Batch size
        """
        if len(normal_traffic_data) == 0:
            logger.warning("No training data provided")
            return
        
        # Convert to numpy array
        data = np.array(normal_traffic_data)
        logger.info(f"Training Autoencoder on {len(data)} samples")
        
        # Training loop
        for epoch in range(epochs):
            total_loss = 0
            num_batches = 0
            
            # Shuffle data
            indices = np.random.permutation(len(data))
            data_shuffled = data[indices]
            
            # Mini-batch training
            for i in range(0, len(data), batch_size):
                batch = data_shuffled[i:i+batch_size]
                batch_tensor = torch.FloatTensor(batch)
                
                # Forward pass
                reconstructed, _ = self.model(batch_tensor)
                loss = self.criterion(reconstructed, batch_tensor)
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                total_loss += loss.item()
                num_batches += 1
            
            avg_loss = total_loss / num_batches if num_batches > 0 else 0
            logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.6f}")
    
    def detect_anomaly(self, features: np.ndarray) -> Tuple[bool, float]:
        """
        Detect anomaly in feature vector
        
        Args:
            features: Feature vector
        
        Returns:
            Tuple of (is_anomaly, anomaly_score)
        """
        self.model.eval()
        with torch.no_grad():
            # Convert to tensor
            if isinstance(features, np.ndarray):
                features_tensor = torch.FloatTensor(features).unsqueeze(0)
            else:
                features_tensor = features
            
            # Calculate reconstruction error
            error = self.model.reconstruction_error(features_tensor)
            error_value = error.item()
            
            # Store error for threshold adaptation
            self.reconstruction_errors.append(error_value)
            if len(self.reconstruction_errors) > 1000:
                self.reconstruction_errors.pop(0)
            
            # Determine if anomaly
            is_anomaly = error_value > self.anomaly_threshold
            
            # Anomaly score (0-1, higher = more anomalous)
            anomaly_score = min(error_value / self.anomaly_threshold, 1.0)
            
            return is_anomaly, anomaly_score
    
    def adapt_threshold(self, percentile: float = 95.0):
        """
        Adapt threshold based on recent reconstruction errors
        
        Args:
            percentile: Percentile to use for threshold (default 95th)
        """
        if len(self.reconstruction_errors) < 100:
            return
        
        threshold = np.percentile(self.reconstruction_errors, percentile)
        self.anomaly_threshold = threshold
        logger.info(f"Adapted anomaly threshold to {threshold:.6f}")

