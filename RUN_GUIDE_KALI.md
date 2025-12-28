# How to Run on Kali Linux

Kali Linux is Debian-based, so the setup is similar to Ubuntu but with some Kali-specific considerations.

## Prerequisites Check

```bash
# Check Python version (should be 3.8+)
python3 --version

# Check if you have root access
sudo whoami
```

## Step 1: Update System

```bash
# Update package lists
sudo apt update

# Upgrade system (optional but recommended)
sudo apt upgrade -y
```

## Step 2: Install System Dependencies

```bash
# Install required packages
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget

# Install networking tools
sudo apt install -y \
    openvswitch-switch \
    openvswitch-common \
    mininet \
    docker.io \
    docker-compose

# Install MQTT broker
sudo apt install -y mosquitto mosquitto-clients

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (optional, to run docker without sudo)
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

## Step 3: Navigate to Project Directory

```bash
# If project is on Windows partition (mounted)
cd /mnt/c/Users/Lenovo/Desktop/eniad\ IRSI/projet\ fog\ final

# Or if copied to Linux home directory
cd ~/fog-project
```

## Step 4: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt
```

## Step 5: Verify Installation

```bash
# Test if key packages are installed
python3 -c "import torch; print('PyTorch:', torch.__version__)"
python3 -c "import ryu; print('Ryu installed')" 2>/dev/null || echo "Ryu not installed yet"
python3 -c "import paho.mqtt.client; print('MQTT client installed')"
python3 -c "import grpc; print('gRPC installed')"

# Test AI models (no network required)
python3 run.py test-ai
```

## Step 6: Start Services

### Option A: Using Docker Compose (Recommended)

```bash
# Start MQTT, Prometheus, and Grafana
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Option B: Manual Service Start

```bash
# Start MQTT broker
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Check MQTT status
sudo systemctl status mosquitto
```

## Step 7: Run the System

### Method 1: Quick Start Script (Easiest)

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Run quick start (as root for network emulation)
sudo bash scripts/quick_start.sh distributed_ai
```

### Method 2: Manual Step-by-Step

Open **4 separate terminal windows/tabs**:

**Terminal 1 - Docker Services:**
```bash
cd /path/to/projet\ fog\ final
docker-compose up -d
```

**Terminal 2 - SDN Controller:**
```bash
cd /path/to/projet\ fog\ final
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

**Terminal 3 - Network Topology:**
```bash
cd /path/to/projet\ fog\ final
source venv/bin/activate
sudo python3 fogbed/topology.py
```

**Terminal 4 - Traffic Generator:**
```bash
cd /path/to/projet\ fog\ final
source venv/bin/activate
python3 iot/traffic_generator.py --pattern periodic --devices 10 --duration 300
```

### Method 3: Using Python Launcher

```bash
# Activate virtual environment first
source venv/bin/activate

# Run controller (in one terminal)
sudo python3 run.py controller --architecture distributed_ai

# Run topology (in another terminal, as root)
sudo python3 run.py topology

# Run traffic (in another terminal)
python3 run.py traffic --pattern periodic --devices 20
```

## Step 8: Run Test Scenarios

```bash
# Activate virtual environment
source venv/bin/activate

# Run all scenarios for an architecture
python3 run.py test --architecture distributed_ai --scenario all --duration 300

# Or use the test script directly
python3 tests/test_scenarios.py --architecture distributed_ai --scenario baseline
```

## Step 9: View Monitoring

### Prometheus
- Open browser: http://localhost:9090
- Query: `fog_node_cpu_usage_percent`

### Grafana
- Open browser: http://localhost:3000
- Login: `admin` / `admin`
- Add data source: http://prometheus:9090

## Kali-Specific Notes

### 1. Firewall Configuration

Kali may have firewall rules that block ports. Check and allow if needed:

```bash
# Check firewall status
sudo ufw status

# Allow required ports (if ufw is active)
sudo ufw allow 6633/tcp    # OpenFlow
sudo ufw allow 1883/tcp    # MQTT
sudo ufw allow 9090/tcp    # Prometheus
sudo ufw allow 3000/tcp    # Grafana
sudo ufw allow 50051/tcp   # gRPC
```

### 2. Network Namespace Issues

If you encounter network namespace errors:

```bash
# Clean up any existing Mininet networks
sudo mn -c

# Check for existing network namespaces
ip netns list

# Remove if needed
sudo ip netns delete <namespace>
```

### 3. Open vSwitch Issues

```bash
# Check OVS status
sudo systemctl status openvswitch-switch

# Start if not running
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch

# Check OVS bridges
sudo ovs-vsctl show
```

### 4. Python Path Issues

If you get import errors:

```bash
# Add project to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or add to your .bashrc
echo 'export PYTHONPATH="${PYTHONPATH}:~/fog-project"' >> ~/.bashrc
source ~/.bashrc
```

## Troubleshooting on Kali

### Issue: "Permission denied" for network operations
```bash
# Ensure you're using sudo for network commands
sudo python3 fogbed/topology.py
```

### Issue: "Ryu not found"
```bash
# Install Ryu
pip install ryu

# Or install from source
git clone https://github.com/faucetsdn/ryu.git
cd ryu
pip install .
```

### Issue: "Mininet not working"
```bash
# Clean Mininet
sudo mn -c

# Test Mininet
sudo mn --test pingall

# If issues persist, reinstall
sudo apt remove mininet
sudo apt install mininet
```

### Issue: "Docker permission denied"
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or:
newgrp docker

# Test
docker ps
```

### Issue: "Port already in use"
```bash
# Find process using port
sudo lsof -i :6633  # Controller
sudo lsof -i :1883  # MQTT
sudo lsof -i :9090  # Prometheus

# Kill process
sudo kill -9 <PID>
```

### Issue: "Module not found" errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Check installation
pip list | grep -E "torch|ryu|paho|grpc"
```

## Stopping the System

```bash
# Use stop script
sudo bash scripts/stop.sh

# Or manually:
# Stop Docker services
docker-compose down

# Kill processes
sudo pkill -f ryu-manager
sudo pkill -f topology.py
sudo pkill -f traffic_generator.py

# Clean Mininet
sudo mn -c
```

## Quick Reference Commands

```bash
# Setup (one-time)
sudo apt update && sudo apt install -y python3-pip python3-venv mininet openvswitch-switch docker.io mosquitto
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start everything
sudo bash scripts/quick_start.sh distributed_ai

# Stop everything
sudo bash scripts/stop.sh

# Test AI models
python3 run.py test-ai

# View logs
tail -f results/logs/*.log
```

## Architecture Selection

You can test all three architectures:

```bash
# Centralized (no AI)
sudo ryu-manager sdn_controller/ryu_apps/centralized_controller.py

# Distributed without AI
sudo ryu-manager sdn_controller/ryu_apps/distributed_controller.py

# Distributed with AI (recommended)
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

## Performance Tips for Kali

1. **Disable unnecessary services** to free resources:
   ```bash
   sudo systemctl disable apache2  # If not needed
   sudo systemctl disable mysql    # If not needed
   ```

2. **Increase swap** if running low on memory:
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Monitor resources**:
   ```bash
   htop
   # or
   watch -n 1 'free -h && echo && df -h'
   ```

## Next Steps

1. Run baseline tests for all three architectures
2. Compare performance metrics
3. Analyze results in `results/metrics/`
4. Create Grafana dashboards for visualization
5. Experiment with different traffic patterns

## Getting Help

- Check logs: `results/logs/`
- View metrics: `results/metrics/`
- Read technical spec: `technical_sheet.tex`
- Check main guide: `RUN_GUIDE.md`

