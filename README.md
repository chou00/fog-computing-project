# AI-Driven Distributed Fog Load Balancing & Anomaly-Aware Routing

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)

A comprehensive implementation of a distributed fog computing architecture with AI-driven load balancing and anomaly-aware routing. This project demonstrates real networking behavior using industry-standard technologies and protocols.

## 🎯 Project Overview

This project implements a **real distributed fog computing architecture** (not a conceptual simulation) that demonstrates mastery of:
- **Fog Computing**: Distributed mesh topology with multiple fog nodes
- **Networking Protocols**: SDN (OpenFlow + Ryu), MQTT, gRPC
- **Artificial Intelligence**: LSTM, Autoencoder, Reinforcement Learning

## 🏗️ Architecture

The system implements **three distinct architectures** for performance comparison:

1. **Centralized Fog** - Single controller with static routing, no AI
2. **Distributed Fog (No AI)** - Rule-based load balancing across multiple nodes
3. **Distributed Fog (With AI)** - Adaptive, predictive, anomaly-aware routing

## ✨ Key Features

- **Real Networking Implementation**: Uses actual SDN protocols (OpenFlow), container-based network emulation
- **AI Integration**: LSTM for load prediction, Autoencoder for anomaly detection, RL for adaptive routing
- **Comprehensive Monitoring**: Prometheus metrics collection and Grafana visualization
- **Three Architecture Comparison**: Quantitative performance analysis with measurable metrics
- **Protocol Implementation**: MQTT for IoT communication, gRPC for fog-to-fog communication

## 🛠️ Technology Stack

### Network Emulation
- **Fogbed** (Containernet + Mininet) - Container-based network emulation
- **Open vSwitch** - Virtual switches for SDN
- **OpenFlow 1.3** - SDN protocol
- **Ryu Controller** - Python-based SDN controller

### AI/ML Components
- **PyTorch/TensorFlow** - Deep learning frameworks
- **LSTM** - Load prediction model
- **Autoencoder** - Anomaly detection model
- **DQN (Deep Q-Network)** - Reinforcement learning agent

### Communication Protocols
- **MQTT** - IoT device messaging (Eclipse Mosquitto)
- **gRPC** - Inter-fog node communication
- **Protocol Buffers** - Serialization

### Monitoring
- **Prometheus** - Time-series metrics collection
- **Grafana** - Visualization and dashboards

## 📋 Prerequisites

- **Linux** (Ubuntu 20.04+, Kali Linux, or WSL2)
- **Python 3.8+**
- **Docker** (optional, for services)
- **Root access** (required for network emulation)
- **8GB+ RAM, 4+ CPU cores** (recommended)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/fog-computing-project.git
cd fog-computing-project
```

### 2. Setup Environment

```bash
# Run setup script
bash scripts/setup.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Services

```bash
# Start MQTT, Prometheus, Grafana
docker-compose up -d
```

### 4. Run the System

**Option A: Quick Start (All-in-One)**
```bash
sudo bash scripts/quick_start.sh distributed_ai
```

**Option B: Step-by-Step (4 Terminals)**

Terminal 1 - Services:
```bash
docker-compose up -d
```

Terminal 2 - SDN Controller:
```bash
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

Terminal 3 - Network Topology:
```bash
source venv/bin/activate
sudo python3 fogbed/topology.py
```

Terminal 4 - Traffic Generator:
```bash
source venv/bin/activate
python3 iot/traffic_generator.py --pattern periodic --devices 10
```

## 📁 Project Structure

```
project/
├── technical_sheet.tex          # Complete technical specification
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Docker services
├── fogbed/                       # Network topology
│   ├── topology.py              # Topology definition
│   └── network_config.py        # Network configuration
├── sdn_controller/              # SDN controllers
│   └── ryu_apps/
│       ├── centralized_controller.py
│       ├── distributed_controller.py
│       └── ai_routing_app.py
├── fog_nodes/                   # Fog node implementations
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
│   └── exporters/
├── tests/                       # Test scenarios
│   └── test_scenarios.py
└── scripts/                     # Setup and deployment scripts
```

## 🧪 Running Tests

```bash
# Test AI models (no network required)
python3 run.py test-ai

# Run test scenarios
python3 run.py test --architecture distributed_ai --scenario baseline

# Run all scenarios
python3 tests/test_scenarios.py --architecture distributed_ai --scenario all
```

## 📊 Performance Metrics

- **Latency**: End-to-end packet latency (mean, p50, p95, p99)
- **Throughput**: Packets/second, bits/second
- **Load Balance**: Standard deviation of node loads
- **Anomaly Detection**: Precision, recall, F1-score
- **Resource Utilization**: CPU, memory, network bandwidth

## 📖 Documentation

- **[Technical Specification](technical_sheet.tex)** - Complete architecture and requirements
- **[Run Guide](RUN_GUIDE.md)** - Detailed setup and execution instructions
- **[Kali Linux Guide](RUN_GUIDE_KALI.md)** - Kali-specific instructions
- **[Quick Start](QUICK_START.md)** - Quick reference guide

## 🔧 Configuration

### Architecture Selection

Choose one of three architectures:

```bash
# Centralized (no AI)
sudo ryu-manager sdn_controller/ryu_apps/centralized_controller.py

# Distributed without AI
sudo ryu-manager sdn_controller/ryu_apps/distributed_controller.py

# Distributed with AI (recommended)
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

### Traffic Patterns

```bash
# Periodic traffic
python3 iot/traffic_generator.py --pattern periodic --devices 20

# Burst traffic
python3 iot/traffic_generator.py --pattern burst --devices 20

# Variable traffic
python3 iot/traffic_generator.py --pattern variable --devices 20
```

## 🐛 Troubleshooting

### Common Issues

**Permission denied**: Use `sudo` for network commands
```bash
sudo python3 fogbed/topology.py
```

**Module not found**: Activate virtual environment
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Port in use**: Find and kill process
```bash
sudo lsof -i :6633
sudo kill -9 <PID>
```

See [RUN_GUIDE.md](RUN_GUIDE.md) for detailed troubleshooting.

## 📈 Results

Test results are saved in `results/metrics/` directory. Compare architectures:

```bash
# View results
cat results/metrics/distributed_ai_baseline.json
```

## 🤝 Contributing

This is an academic/engineering project. For improvements or bug fixes:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

Engineering Project - Academic Use

## 🙏 Acknowledgments

- Fogbed/Containernet for network emulation
- Ryu SDN Framework
- PyTorch and TensorFlow communities
- Open vSwitch project

## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

**Note**: This project requires Linux for full functionality. Windows users should use WSL2 or a Linux VM.
