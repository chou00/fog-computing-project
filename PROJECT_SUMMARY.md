# AI-Driven Distributed Fog Load Balancing & Anomaly-Aware Routing

## Project Summary

This project implements a comprehensive distributed fog computing architecture with AI-driven load balancing and anomaly-aware routing. The system demonstrates real networking behavior using industry-standard technologies and protocols.

## Architecture Overview

The project implements three distinct architectures for comparison:

1. **Centralized Fog**: Single controller with static routing, no AI
2. **Distributed Fog (No AI)**: Rule-based load balancing across multiple nodes
3. **Distributed Fog (With AI)**: Adaptive, predictive, anomaly-aware routing

## Key Components

### Network Infrastructure
- **Fogbed/Containernet**: Container-based network emulation
- **Open vSwitch**: Virtual switches for SDN
- **OpenFlow 1.3**: SDN protocol
- **Ryu Controller**: Python-based SDN controller

### AI Components
- **LSTM Load Predictor**: Predicts future node load based on historical metrics
- **Autoencoder Anomaly Detector**: Detects network anomalies in real-time
- **DQN RL Agent**: Makes intelligent routing decisions using reinforcement learning

### Communication Protocols
- **MQTT**: IoT device messaging (Eclipse Mosquitto)
- **gRPC**: Inter-fog node communication
- **Protocol Buffers**: Serialization for gRPC

### Monitoring
- **Prometheus**: Time-series metrics collection
- **Grafana**: Visualization and dashboards
- **Custom Exporters**: Fog node metrics export

## Project Structure

```
project/
├── technical_sheet.tex          # Complete technical specification
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker services (MQTT, Prometheus, Grafana)
├── fogbed/                       # Network topology
│   ├── topology.py              # Topology definition
│   └── network_config.py        # Network configuration
├── sdn_controller/              # SDN controllers
│   └── ryu_apps/
│       ├── centralized_controller.py
│       ├── distributed_controller.py
│       └── ai_routing_app.py
├── fog_nodes/                   # Fog node implementations
│   ├── node_base.py
│   ├── fog_node.py              # Complete fog node
│   ├── load_monitor.py
│   └── grpc_service.py
├── ai_models/                   # AI/ML models
│   ├── lstm/model.py
│   ├── autoencoder/model.py
│   └── rl/dqn_agent.py
├── iot/                         # IoT components
│   ├── mqtt_client.py
│   └── traffic_generator.py
├── monitoring/                  # Monitoring setup
│   ├── prometheus/
│   ├── grafana/
│   └── exporters/
└── tests/                       # Test scenarios
    └── test_scenarios.py
```

## Quick Start

### Prerequisites
- Linux (Ubuntu 20.04+ recommended)
- Python 3.8+
- Docker (optional)
- Root access (for Mininet)

### Installation

```bash
# Setup environment
bash scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the System

```bash
# Deploy centralized architecture
sudo bash scripts/deploy.sh centralized

# Deploy distributed architecture without AI
sudo bash scripts/deploy.sh distributed_no_ai

# Deploy distributed architecture with AI
sudo bash scripts/deploy.sh distributed_ai
```

### Running Tests

```bash
# Run all test scenarios for an architecture
python tests/test_scenarios.py --architecture distributed_ai --scenario all

# Run specific scenario
python tests/test_scenarios.py --architecture distributed_ai --scenario baseline
```

## Test Scenarios

1. **Baseline Performance**: Steady-state traffic, measure baseline metrics
2. **Traffic Burst**: Sudden traffic increase (2x, 5x, 10x)
3. **Node Failure**: Random node failure, measure recovery
4. **Anomaly Injection**: Inject network anomalies, test detection
5. **Scalability**: Vary number of nodes and devices
6. **Dynamic Load**: Variable traffic patterns over time

## Performance Metrics

- **Latency**: End-to-end packet latency (mean, p50, p95, p99)
- **Throughput**: Packets/second, bits/second
- **Load Balance**: Standard deviation of node loads
- **Anomaly Detection**: Precision, recall, F1-score
- **Resource Utilization**: CPU, memory, network bandwidth

## Key Features

### Real Networking Implementation
- Uses actual SDN protocols (OpenFlow)
- Real container-based network emulation
- Measurable performance metrics

### AI Integration
- Predictive load balancing using LSTM
- Real-time anomaly detection
- Adaptive routing with reinforcement learning

### Comprehensive Monitoring
- Prometheus metrics collection
- Grafana dashboards
- Real-time visualization

### Three Architecture Comparison
- Quantitative performance comparison
- Clear trade-offs identification
- Statistical significance

## Technical Highlights

1. **Distributed Mesh Topology**: Real mesh network with multiple fog nodes
2. **SDN-Based Routing**: Dynamic routing using OpenFlow
3. **AI-Driven Decisions**: LSTM, Autoencoder, and RL working together
4. **Protocol Implementation**: MQTT and gRPC for real communication
5. **Monitoring Integration**: Prometheus and Grafana for metrics

## Next Steps

1. Generate Protocol Buffer files for gRPC
2. Create Docker images for fog nodes and IoT devices
3. Implement complete topology discovery
4. Add more sophisticated RL reward functions
5. Create Grafana dashboards
6. Implement comprehensive test scenarios

## Notes

- The technical specification (`technical_sheet.tex`) is the authoritative reference
- All implementations follow the architecture defined in the technical sheet
- The system is designed for real networking behavior, not simulation
- Performance metrics are collected and can be compared across architectures

## License

Engineering Project - Academic Use

