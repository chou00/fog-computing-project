# How to Run the Fog Computing Project

## Prerequisites

Before running the project, ensure you have:

1. **Linux Operating System** (Ubuntu 20.04+ recommended)
   - Windows users: Use WSL2 or a Linux VM
   - The project requires root access for Mininet/network emulation

2. **Python 3.8 or higher**
   ```bash
   python3 --version
   ```

3. **System Dependencies** (Ubuntu/Debian):
   ```bash
   sudo apt-get update
   sudo apt-get install -y \
       python3-pip \
       python3-dev \
       build-essential \
       libssl-dev \
       libffi-dev \
       openvswitch-switch \
       openvswitch-common \
       mininet \
       docker.io \
       docker-compose \
       mosquitto \
       mosquitto-clients
   ```

## Step 1: Setup Environment

### Clone/Navigate to Project Directory
```bash
cd "path/to/projet fog final"
```

### Run Setup Script
```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run setup (creates virtual environment and installs dependencies)
bash scripts/setup.sh
```

### Activate Virtual Environment
```bash
source venv/bin/activate
```

If the setup script doesn't work, manually install:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: Start Supporting Services

### Option A: Using Docker Compose (Recommended)
```bash
# Start MQTT broker, Prometheus, and Grafana
docker-compose up -d

# Check services are running
docker-compose ps
```

### Option B: Manual Service Start
```bash
# Start MQTT broker
mosquitto -d

# Start Prometheus (in another terminal)
prometheus --config.file=monitoring/prometheus/prometheus.yml &
```

## Step 3: Start SDN Controller

Open a **new terminal** (keep it running) and run one of the following based on the architecture you want to test:

### Architecture 1: Centralized (No AI)
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/centralized_controller.py
```

### Architecture 2: Distributed (No AI)
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/distributed_controller.py
```

### Architecture 3: Distributed with AI
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

**Note**: The controller must be running before starting the network topology.

## Step 4: Start Network Topology

Open **another terminal** and run:

```bash
cd "path/to/projet fog final"
source venv/bin/activate

# Run as root (required for Mininet)
sudo python3 fogbed/topology.py
```

Or use the deployment script:

```bash
# For centralized architecture
sudo bash scripts/deploy.sh centralized

# For distributed without AI
sudo bash scripts/deploy.sh distributed_no_ai

# For distributed with AI
sudo bash scripts/deploy.sh distributed_ai
```

## Step 5: Start IoT Traffic Generator

Open **another terminal** and run:

```bash
cd "path/to/projet fog final"
source venv/bin/activate

# Periodic traffic (default)
python3 iot/traffic_generator.py --pattern periodic --devices 20 --duration 300

# Burst traffic
python3 iot/traffic_generator.py --pattern burst --devices 20 --duration 300

# Variable traffic
python3 iot/traffic_generator.py --pattern variable --devices 20 --duration 300
```

## Step 6: Start Fog Nodes

For each fog node, open a terminal and run:

```bash
cd "path/to/projet fog final"
source venv/bin/activate

# Fog node 1 (centralized architecture)
python3 fog_nodes/fog_node.py --node-id fog1 --architecture centralized --grpc-port 50051 --prometheus-port 9090

# Fog node 2 (distributed without AI)
python3 fog_nodes/fog_node.py --node-id fog2 --architecture distributed_no_ai --grpc-port 50052 --prometheus-port 9091

# Fog node 3 (distributed with AI)
python3 fog_nodes/fog_node.py --node-id fog3 --architecture distributed_ai --grpc-port 50053 --prometheus-port 9092
```

## Step 7: Run Test Scenarios

In a new terminal:

```bash
cd "path/to/projet fog final"
source venv/bin/activate

# Run all test scenarios for an architecture
python3 tests/test_scenarios.py --architecture distributed_ai --scenario all --duration 300

# Run specific scenario
python3 tests/test_scenarios.py --architecture distributed_ai --scenario baseline --duration 300
python3 tests/test_scenarios.py --architecture distributed_ai --scenario burst --duration 300
python3 tests/test_scenarios.py --architecture distributed_ai --scenario failure --duration 300
```

## Step 8: View Monitoring

### Prometheus
- Open browser: http://localhost:9090
- Query metrics: `fog_node_cpu_usage_percent`, `fog_node_latency_seconds`, etc.

### Grafana
- Open browser: http://localhost:3000
- Login: admin / admin
- Add Prometheus data source: http://prometheus:9090
- Create dashboards for fog node metrics

## Quick Start (All-in-One)

For a quick test, run these commands in separate terminals:

**Terminal 1 - Services:**
```bash
docker-compose up -d
```

**Terminal 2 - SDN Controller:**
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

**Terminal 3 - Network Topology:**
```bash
cd "path/to/projet fog final"
source venv/bin/activate
sudo python3 fogbed/topology.py
```

**Terminal 4 - Traffic Generator:**
```bash
cd "path/to/projet fog final"
source venv/bin/activate
python3 iot/traffic_generator.py --pattern periodic --devices 10 --duration 60
```

## Troubleshooting

### Issue: "Permission denied" or "Operation not permitted"
**Solution**: Run network-related commands with `sudo`

### Issue: "Module not found" errors
**Solution**: 
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Port already in use"
**Solution**: 
```bash
# Find and kill process using the port
sudo lsof -i :6633  # Ryu controller
sudo lsof -i :1883  # MQTT
sudo kill -9 <PID>
```

### Issue: "Ryu controller not connecting"
**Solution**: 
- Ensure controller is running before starting topology
- Check OpenFlow version matches (OpenFlow 1.3)
- Verify switch configuration in topology.py

### Issue: "MQTT connection failed"
**Solution**:
```bash
# Check MQTT broker is running
sudo systemctl status mosquitto

# Start if not running
sudo systemctl start mosquitto
```

### Issue: "Docker containers not starting"
**Solution**:
```bash
# Check Docker is running
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Restart containers
docker-compose down
docker-compose up -d
```

## Stopping the System

1. **Stop traffic generator**: Press `Ctrl+C` in traffic generator terminal
2. **Stop network topology**: Press `Ctrl+C` in topology terminal, then run cleanup
3. **Stop SDN controller**: Press `Ctrl+C` in controller terminal
4. **Stop services**:
   ```bash
   docker-compose down
   # or
   sudo pkill mosquitto
   sudo pkill prometheus
   ```

## Viewing Results

Test results are saved in:
```
results/metrics/
```

View with:
```bash
cat results/metrics/<architecture>_<scenario>.json
```

## Next Steps

1. **Compare Architectures**: Run tests for all three architectures and compare results
2. **Customize Topology**: Modify `fogbed/topology.py` to change number of nodes/devices
3. **Tune AI Models**: Adjust hyperparameters in `ai_models/` for better performance
4. **Create Dashboards**: Build Grafana dashboards for visualization
5. **Add More Scenarios**: Extend `tests/test_scenarios.py` with custom tests

## Notes

- **Root Access Required**: Network emulation (Mininet) requires root privileges
- **Multiple Terminals**: Keep controller, topology, and traffic generator in separate terminals
- **Resource Usage**: The system can be resource-intensive; ensure adequate CPU/RAM
- **Linux Only**: This project is designed for Linux; Windows users need WSL2 or VM

