#!/bin/bash
# Setup script for Fog Computing Project

set -e

echo "=== Fog Computing Project Setup ==="

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3 is required"; exit 1; }

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install system dependencies (Ubuntu/Debian)
if [ -f /etc/debian_version ]; then
    echo "Installing system dependencies..."
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
        docker-compose
fi

# Generate gRPC code (if proto files exist)
if [ -f "fog_nodes/fog_proto.proto" ]; then
    echo "Generating gRPC code..."
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. fog_nodes/fog_proto.proto
fi

# Create necessary directories
echo "Creating directories..."
mkdir -p results/metrics
mkdir -p results/logs
mkdir -p data/models

# Set permissions
chmod +x scripts/*.sh

echo "=== Setup Complete ==="
echo "To activate the virtual environment, run: source venv/bin/activate"

