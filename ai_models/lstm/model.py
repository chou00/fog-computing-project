"""
LSTM Model for Load Prediction
Predicts future load based on historical metrics
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple
from loguru import logger


class LSTMLoadPredictor(nn.Module):
    """LSTM model for predicting future node load"""
    
    def __init__(self, input_size: int = 5, hidden_size: int = 64, num_layers: int = 2, 
                 dropout: float = 0.2, output_size: int = 1):
        """
        Initialize LSTM predictor
        
        Args:
            input_size: Number of input features (e.g., cpu, memory, network_in, network_out, connections)
            hidden_size: LSTM hidden layer size
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            output_size: Number of output predictions (1 for load score)
        """
        super(LSTMLoadPredictor, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # LSTM layers
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )
        
        # Fully connected output layer
        self.fc = nn.Linear(hidden_size, output_size)
        self.dropout = nn.Dropout(dropout)
        
        logger.info(f"LSTM Load Predictor initialized: input_size={input_size}, "
                   f"hidden_size={hidden_size}, num_layers={num_layers}")
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass
        
        Args:
            x: Input tensor of shape (batch_size, sequence_length, input_size)
        
        Returns:
            Predicted load tensor of shape (batch_size, output_size)
        """
        # LSTM forward pass
        lstm_out, _ = self.lstm(x)
        
        # Take the last output from the sequence
        last_output = lstm_out[:, -1, :]
        
        # Apply dropout
        last_output = self.dropout(last_output)
        
        # Fully connected layer
        output = self.fc(last_output)
        
        # Apply sigmoid to get load score between 0 and 1
        output = torch.sigmoid(output)
        
        return output
    
    def predict(self, sequence: np.ndarray) -> float:
        """
        Predict load from a sequence of metrics
        
        Args:
            sequence: Array of shape (sequence_length, input_size)
        
        Returns:
            Predicted load score (0-1)
        """
        self.eval()
        with torch.no_grad():
            # Convert to tensor and add batch dimension
            if isinstance(sequence, np.ndarray):
                sequence = torch.FloatTensor(sequence)
            
            if sequence.dim() == 2:
                sequence = sequence.unsqueeze(0)  # Add batch dimension
            
            # Make prediction
            prediction = self.forward(sequence)
            
            # Return scalar value
            return prediction.item()
    
    def train_step(self, sequences: np.ndarray, targets: np.ndarray, 
                   optimizer: torch.optim.Optimizer, criterion: nn.Module) -> float:
        """
        Perform one training step
        
        Args:
            sequences: Input sequences of shape (batch_size, sequence_length, input_size)
            targets: Target load scores of shape (batch_size, 1)
            optimizer: Optimizer
            criterion: Loss function
        
        Returns:
            Loss value
        """
        self.train()
        
        # Convert to tensors
        if isinstance(sequences, np.ndarray):
            sequences = torch.FloatTensor(sequences)
        if isinstance(targets, np.ndarray):
            targets = torch.FloatTensor(targets)
        
        # Forward pass
        predictions = self.forward(sequences)
        
        # Calculate loss
        loss = criterion(predictions, targets)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        
        # Gradient clipping
        torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=1.0)
        
        optimizer.step()
        
        return loss.item()


class LoadPredictor:
    """Wrapper class for LSTM load prediction with training and inference"""
    
    def __init__(self, input_size: int = 5, hidden_size: int = 64, 
                 num_layers: int = 2, sequence_length: int = 60, 
                 learning_rate: float = 0.001):
        """
        Initialize load predictor
        
        Args:
            input_size: Number of input features
            hidden_size: LSTM hidden size
            num_layers: Number of LSTM layers
            sequence_length: Length of input sequence (time steps)
            learning_rate: Learning rate for training
        """
        self.sequence_length = sequence_length
        self.input_size = input_size
        
        # Initialize model
        self.model = LSTMLoadPredictor(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers
        )
        
        # Optimizer and loss
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        self.criterion = nn.MSELoss()
        
        logger.info(f"Load Predictor initialized with sequence_length={sequence_length}")
    
    def prepare_sequences(self, metrics_history: List) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare training sequences from metrics history
        
        Args:
            metrics_history: List of NodeMetrics objects
        
        Returns:
            Tuple of (sequences, targets) as numpy arrays
        """
        if len(metrics_history) < self.sequence_length + 1:
            return np.array([]), np.array([])
        
        sequences = []
        targets = []
        
        # Create sliding windows
        for i in range(len(metrics_history) - self.sequence_length):
            # Input sequence
            sequence = []
            for j in range(self.sequence_length):
                metrics = metrics_history[i + j]
                # Extract features: [cpu, memory, network_in, network_out, connections]
                features = [
                    metrics.cpu_usage / 100.0,
                    metrics.memory_usage / 100.0,
                    min(metrics.network_in / 1e6, 1.0),
                    min(metrics.network_out / 1e6, 1.0),
                    min(metrics.active_connections / 100.0, 1.0)
                ]
                sequence.append(features)
            
            # Target (next time step load score)
            target_metrics = metrics_history[i + self.sequence_length]
            target = (
                target_metrics.cpu_usage / 100.0 * 0.3 +
                target_metrics.memory_usage / 100.0 * 0.3 +
                min((target_metrics.network_in + target_metrics.network_out) / 2e6, 1.0) * 0.2 +
                min(target_metrics.active_connections / 100.0, 1.0) * 0.2
            )
            
            sequences.append(sequence)
            targets.append([target])
        
        return np.array(sequences), np.array(targets)
    
    def train(self, metrics_history: List, epochs: int = 10, batch_size: int = 32):
        """
        Train the model on metrics history
        
        Args:
            metrics_history: List of NodeMetrics objects
            epochs: Number of training epochs
            batch_size: Batch size for training
        """
        sequences, targets = self.prepare_sequences(metrics_history)
        
        if len(sequences) == 0:
            logger.warning("Not enough data for training")
            return
        
        logger.info(f"Training LSTM on {len(sequences)} sequences")
        
        # Training loop
        for epoch in range(epochs):
            total_loss = 0
            num_batches = 0
            
            # Shuffle data
            indices = np.random.permutation(len(sequences))
            sequences_shuffled = sequences[indices]
            targets_shuffled = targets[indices]
            
            # Mini-batch training
            for i in range(0, len(sequences), batch_size):
                batch_sequences = sequences_shuffled[i:i+batch_size]
                batch_targets = targets_shuffled[i:i+batch_size]
                
                loss = self.model.train_step(
                    batch_sequences, batch_targets, 
                    self.optimizer, self.criterion
                )
                
                total_loss += loss
                num_batches += 1
            
            avg_loss = total_loss / num_batches if num_batches > 0 else 0
            logger.info(f"Epoch {epoch+1}/{epochs}, Loss: {avg_loss:.4f}")
    
    def predict_next_load(self, metrics_history: List) -> float:
        """
        Predict next time step load
        
        Args:
            metrics_history: List of recent NodeMetrics objects (at least sequence_length)
        
        Returns:
            Predicted load score (0-1)
        """
        if len(metrics_history) < self.sequence_length:
            # Not enough history, return current load
            if len(metrics_history) > 0:
                latest = metrics_history[-1]
                return (
                    latest.cpu_usage / 100.0 * 0.3 +
                    latest.memory_usage / 100.0 * 0.3 +
                    min((latest.network_in + latest.network_out) / 2e6, 1.0) * 0.2 +
                    min(latest.active_connections / 100.0, 1.0) * 0.2
                )
            return 0.5  # Default
        
        # Prepare sequence
        sequence = []
        for metrics in metrics_history[-self.sequence_length:]:
            features = [
                metrics.cpu_usage / 100.0,
                metrics.memory_usage / 100.0,
                min(metrics.network_in / 1e6, 1.0),
                min(metrics.network_out / 1e6, 1.0),
                min(metrics.active_connections / 100.0, 1.0)
            ]
            sequence.append(features)
        
        sequence = np.array(sequence)
        prediction = self.model.predict(sequence)
        
        return prediction

