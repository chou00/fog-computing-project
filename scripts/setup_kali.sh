#!/bin/bash
# Setup script specifically for Kali Linux

set -e

echo "=== Fog Computing Project Setup for Kali Linux ==="

# Check if running as root for some operations
if [ "$EUID" -eq 0 ]; then 
    echo "Running as root - some operations will be done directly"
    SUDO=""
else
    SUDO="sudo"
    echo "Will use sudo for system operations"
fi

# Update package lists
echo "Updating package lists..."
$SUDO apt update

# Install system dependencies
echo "Installing system dependencies..."
$SUDO apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    build-essential \
    libssl-dev \
    libffi-dev \
    git \
    curl \
    wget \
    openvswitch-switch \
    openvswitch-common \
    mininet \
    docker.io \
    docker-compose \
    mosquitto \
    mosquitto-clients

# Start and enable Docker
echo "Configuring Docker..."
$SUDO systemctl start docker
$SUDO systemctl enable docker

# Start and enable Open vSwitch
echo "Configuring Open vSwitch..."
$SUDO systemctl start openvswitch-switch
$SUDO systemctl enable openvswitch-switch

# Start and enable Mosquitto
echo "Configuring Mosquitto..."
$SUDO systemctl start mosquitto
$SUDO systemctl enable mosquitto

# Create virtual environment
echo "Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p results/metrics
mkdir -p results/logs
mkdir -p data/models

# Set permissions for scripts
echo "Setting script permissions..."
chmod +x scripts/*.sh 2>/dev/null || true

# Clean Mininet (if exists)
echo "Cleaning Mininet..."
$SUDO mn -c 2>/dev/null || true

# Test installations
echo ""
echo "=== Testing Installations ==="

# Test Python
python3 --version

# Test PyTorch
python3 -c "import torch; print('✓ PyTorch:', torch.__version__)" 2>/dev/null || echo "✗ PyTorch not installed"

# Test Ryu
python3 -c "import ryu; print('✓ Ryu installed')" 2>/dev/null || echo "✗ Ryu not installed"

# Test MQTT
python3 -c "import paho.mqtt.client; print('✓ MQTT client installed')" 2>/dev/null || echo "✗ MQTT client not installed"

# Test gRPC
python3 -c "import grpc; print('✓ gRPC installed')" 2>/dev/null || echo "✗ gRPC not installed"

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the system, run:"
echo "  sudo bash scripts/quick_start.sh distributed_ai"
echo ""
echo "Note: Network operations require root access (sudo)"

