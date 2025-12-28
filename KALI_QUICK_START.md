# Quick Start Guide for Kali Linux

## Step 1: Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    openvswitch-switch \
    openvswitch-common \
    mininet \
    docker.io \
    docker-compose \
    mosquitto \
    mosquitto-clients

# Start services
sudo systemctl start docker
sudo systemctl enable docker
sudo systemctl start openvswitch-switch
sudo systemctl enable openvswitch-switch
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

## Step 2: Clone or Navigate to Project

```bash
# If cloning from GitHub
git clone https://github.com/chou00/fog-computing-project.git
cd fog-computing-project

# Or if you already have it locally
cd /path/to/fog-computing-project
```

## Step 3: Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Quick Start (All-in-One)

```bash
# Make scripts executable
chmod +x scripts/*.sh

# Start everything with one command
sudo bash scripts/quick_start.sh distributed_ai
```

This will start:
- Docker services (MQTT, Prometheus, Grafana)
- SDN Controller
- Network Topology
- Traffic Generator

## Step 5: Or Run Step-by-Step (4 Terminals)

### Terminal 1 - Docker Services
```bash
cd fog-computing-project
docker-compose up -d
```

### Terminal 2 - SDN Controller
```bash
cd fog-computing-project
source venv/bin/activate
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

### Terminal 3 - Network Topology
```bash
cd fog-computing-project
source venv/bin/activate
sudo python3 fogbed/topology.py
```

### Terminal 4 - Traffic Generator
```bash
cd fog-computing-project
source venv/bin/activate
python3 iot/traffic_generator.py --pattern periodic --devices 10 --duration 300
```

## Step 6: Test AI Models (No Network Required)

```bash
source venv/bin/activate
python3 run.py test-ai
```

## Step 7: View Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

## Kali-Specific Notes

### Clean Mininet Before Starting
```bash
sudo mn -c
```

### Check Services Status
```bash
# Check Open vSwitch
sudo systemctl status openvswitch-switch

# Check MQTT
sudo systemctl status mosquitto

# Check Docker
sudo systemctl status docker
```

### Firewall (if enabled)
```bash
# Allow required ports
sudo ufw allow 6633/tcp    # OpenFlow
sudo ufw allow 1883/tcp     # MQTT
sudo ufw allow 9090/tcp     # Prometheus
sudo ufw allow 3000/tcp      # Grafana
```

## Troubleshooting

### "Permission denied"
```bash
# Use sudo for network commands
sudo python3 fogbed/topology.py
```

### "Port already in use"
```bash
# Find process
sudo lsof -i :6633

# Kill process
sudo kill -9 <PID>
```

### "Module not found"
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "Mininet not working"
```bash
# Clean first
sudo mn -c

# Test Mininet
sudo mn --test pingall
```

## Stop the System

```bash
# Use stop script
sudo bash scripts/stop.sh

# Or manually
sudo pkill -f ryu-manager
sudo pkill -f topology.py
sudo pkill -f traffic_generator.py
sudo mn -c
docker-compose down
```

## Architecture Options

Choose one of three architectures:

```bash
# Centralized (no AI)
sudo ryu-manager sdn_controller/ryu_apps/centralized_controller.py

# Distributed without AI
sudo ryu-manager sdn_controller/ryu_apps/distributed_controller.py

# Distributed with AI (recommended)
sudo ryu-manager sdn_controller/ryu_apps/ai_routing_app.py
```

## Complete Setup Script

For automated setup, use the Kali-specific script:

```bash
bash scripts/setup_kali.sh
```

This will install all dependencies and set up the environment automatically.

## Quick Reference

```bash
# Setup (one-time)
bash scripts/setup_kali.sh
source venv/bin/activate

# Start
sudo bash scripts/quick_start.sh distributed_ai

# Stop
sudo bash scripts/stop.sh

# Test AI
python3 run.py test-ai
```

---

For detailed instructions, see [RUN_GUIDE_KALI.md](RUN_GUIDE_KALI.md)

