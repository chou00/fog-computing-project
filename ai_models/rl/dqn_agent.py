"""
Deep Q-Network (DQN) Agent for Intelligent Routing
Makes routing decisions based on current state and learned policy
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque
import random
from typing import List, Tuple, Optional
from loguru import logger


class DQNNetwork(nn.Module):
    """Deep Q-Network for routing decisions"""
    
    def __init__(self, state_size: int, action_size: int, hidden_sizes: List[int] = [128, 64]):
        """
        Initialize DQN network
        
        Args:
            state_size: Size of state vector
            action_size: Number of possible actions (next hops)
            hidden_sizes: List of hidden layer sizes
        """
        super(DQNNetwork, self).__init__()
        
        layers = []
        prev_size = state_size
        
        for hidden_size in hidden_sizes:
            layers.extend([
                nn.Linear(prev_size, hidden_size),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, action_size))
        self.network = nn.Sequential(*layers)
        
        logger.info(f"DQN Network initialized: state_size={state_size}, "
                   f"action_size={action_size}")
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        return self.network(state)


class DQNAgent:
    """DQN Agent for routing decisions"""
    
    def __init__(self, state_size: int, action_size: int, 
                 learning_rate: float = 0.001, gamma: float = 0.95,
                 epsilon: float = 1.0, epsilon_min: float = 0.01,
                 epsilon_decay: float = 0.995, memory_size: int = 10000,
                 batch_size: int = 32, target_update_freq: int = 100):
        """
        Initialize DQN agent
        
        Args:
            state_size: Size of state vector
            action_size: Number of possible actions
            learning_rate: Learning rate
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_min: Minimum exploration rate
            epsilon_decay: Epsilon decay rate
            memory_size: Replay buffer size
            batch_size: Training batch size
            target_update_freq: Frequency of target network updates
        """
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size
        self.target_update_freq = target_update_freq
        self.update_counter = 0
        
        # Neural networks
        self.q_network = DQNNetwork(state_size, action_size)
        self.target_network = DQNNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Copy weights to target network
        self.update_target_network()
        
        # Replay buffer
        self.memory = deque(maxlen=memory_size)
        
        logger.info(f"DQN Agent initialized: state_size={state_size}, "
                   f"action_size={action_size}, epsilon={epsilon}")
    
    def update_target_network(self):
        """Copy weights from Q-network to target network"""
        self.target_network.load_state_dict(self.q_network.state_dict())
    
    def remember(self, state: np.ndarray, action: int, reward: float, 
                 next_state: np.ndarray, done: bool):
        """
        Store experience in replay buffer
        
        Args:
            state: Current state
            action: Action taken
            reward: Reward received
            next_state: Next state
            done: Whether episode is done
        """
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state: np.ndarray, training: bool = True) -> int:
        """
        Choose action using epsilon-greedy policy
        
        Args:
            state: Current state vector
            training: Whether in training mode
        
        Returns:
            Selected action (next hop index)
        """
        if training and random.random() <= self.epsilon:
            # Exploration: random action
            return random.randrange(self.action_size)
        
        # Exploitation: use Q-network
        self.q_network.eval()
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            action = q_values.argmax().item()
        
        return action
    
    def replay(self) -> Optional[float]:
        """
        Train the agent on a batch of experiences
        
        Returns:
            Loss value if training occurred, None otherwise
        """
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch from replay buffer
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(states))
        actions = torch.LongTensor(actions)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(np.array(next_states))
        dones = torch.FloatTensor(dones)
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1))
        
        # Next Q values from target network
        next_q_values = self.target_network(next_states).max(1)[0].detach()
        target_q_values = rewards + (self.gamma * next_q_values * (1 - dones))
        
        # Compute loss
        loss = nn.functional.mse_loss(current_q_values.squeeze(), target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        self.optimizer.step()
        
        # Update target network periodically
        self.update_counter += 1
        if self.update_counter % self.target_update_freq == 0:
            self.update_target_network()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def build_state(self, current_node_metrics, predicted_load: float, 
                    neighbor_states: List[dict], anomaly_score: float) -> np.ndarray:
        """
        Build state vector from current information
        
        Args:
            current_node_metrics: Current node metrics
            predicted_load: Predicted future load
            neighbor_states: List of neighbor node states
            anomaly_score: Current anomaly score
        
        Returns:
            State vector
        """
        state = []
        
        # Current node features
        if current_node_metrics:
            state.extend([
                current_node_metrics.cpu_usage / 100.0,
                current_node_metrics.memory_usage / 100.0,
                min(current_node_metrics.network_in / 1e6, 1.0),
                min(current_node_metrics.network_out / 1e6, 1.0),
                min(current_node_metrics.active_connections / 100.0, 1.0)
            ])
        else:
            state.extend([0.0] * 5)
        
        # Predicted load
        state.append(predicted_load)
        
        # Anomaly score
        state.append(anomaly_score)
        
        # Neighbor information (up to 5 neighbors)
        max_neighbors = 5
        for i in range(max_neighbors):
            if i < len(neighbor_states):
                neighbor = neighbor_states[i]
                state.extend([
                    neighbor.get('load', 0.0),
                    neighbor.get('latency', 0.0) / 100.0,  # Normalize
                    neighbor.get('anomaly_score', 0.0)
                ])
            else:
                state.extend([0.0, 0.0, 0.0])
        
        # Pad or truncate to state_size
        if len(state) < self.state_size:
            state.extend([0.0] * (self.state_size - len(state)))
        elif len(state) > self.state_size:
            state = state[:self.state_size]
        
        return np.array(state)
    
    def calculate_reward(self, latency: float, load_balance: float, 
                        anomaly_penalty: float, packet_delivered: bool) -> float:
        """
        Calculate reward for routing decision
        
        Args:
            latency: Packet latency (ms)
            load_balance: Load balance score (lower is better)
            anomaly_penalty: Penalty for routing through anomalous paths
            packet_delivered: Whether packet was successfully delivered
        
        Returns:
            Reward value
        """
        if not packet_delivered:
            return -10.0  # Large penalty for packet loss
        
        # Reward components
        latency_reward = -latency / 100.0  # Normalize, negative because lower is better
        balance_reward = -load_balance * 2.0  # Penalize imbalance
        anomaly_reward = -anomaly_penalty * 5.0  # Large penalty for anomalies
        
        total_reward = latency_reward + balance_reward + anomaly_reward
        
        return total_reward
    
    def save(self, filepath: str):
        """Save model to file"""
        torch.save({
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon
        }, filepath)
        logger.info(f"DQN Agent saved to {filepath}")
    
    def load(self, filepath: str):
        """Load model from file"""
        checkpoint = torch.load(filepath)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint.get('epsilon', self.epsilon_min)
        logger.info(f"DQN Agent loaded from {filepath}")

