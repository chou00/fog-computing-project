#!/bin/bash
# Deployment script for Fog Computing Project

set -e

echo "=== Fog Computing Project Deployment ==="

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Check if running as root (required for Mininet)
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo) for network emulation"
    exit 1
fi

# Architecture selection
ARCHITECTURE=${1:-distributed_ai}

if [ "$ARCHITECTURE" != "centralized" ] && \
   [ "$ARCHITECTURE" != "distributed_no_ai" ] && \
   [ "$ARCHITECTURE" != "distributed_ai" ]; then
    echo "Invalid architecture. Use: centralized, distributed_no_ai, or distributed_ai"
    exit 1
fi

echo "Deploying architecture: $ARCHITECTURE"

# Start MQTT broker (if not running)
if ! pgrep -x "mosquitto" > /dev/null; then
    echo "Starting MQTT broker..."
    mosquitto -d || echo "MQTT broker already running or not installed"
fi

# Start Prometheus (if using)
if [ -f "monitoring/prometheus/prometheus.yml" ]; then
    echo "Starting Prometheus..."
    prometheus --config.file=monitoring/prometheus/prometheus.yml &
    PROMETHEUS_PID=$!
    echo "Prometheus started with PID: $PROMETHEUS_PID"
fi

# Start Ryu controller based on architecture
echo "Starting SDN controller for architecture: $ARCHITECTURE"

case $ARCHITECTURE in
    centralized)
        ryu-manager sdn_controller/ryu_apps/centralized_controller.py &
        RYU_PID=$!
        ;;
    distributed_no_ai)
        ryu-manager sdn_controller/ryu_apps/distributed_controller.py &
        RYU_PID=$!
        ;;
    distributed_ai)
        ryu-manager sdn_controller/ryu_apps/ai_routing_app.py &
        RYU_PID=$!
        ;;
esac

echo "Ryu controller started with PID: $RYU_PID"

# Wait a moment for controller to start
sleep 2

# Start network topology
echo "Starting network topology..."
python3 fogbed/topology.py --architecture $ARCHITECTURE &
TOPOLOGY_PID=$!

echo "Network topology started with PID: $TOPOLOGY_PID"

echo "=== Deployment Complete ==="
echo "Architecture: $ARCHITECTURE"
echo "Ryu Controller PID: $RYU_PID"
echo "Topology PID: $TOPOLOGY_PID"
echo ""
echo "To stop, run: sudo pkill -f ryu-manager && sudo pkill -f topology.py"

