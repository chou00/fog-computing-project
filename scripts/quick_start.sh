#!/bin/bash
# Quick Start Script for Fog Computing Project

set -e

echo "=== Fog Computing Project - Quick Start ==="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo) for network emulation"
    exit 1
fi

# Architecture selection (default: distributed_ai)
ARCHITECTURE=${1:-distributed_ai}

echo "Starting architecture: $ARCHITECTURE"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Start Docker services
echo "Starting Docker services (MQTT, Prometheus, Grafana)..."
docker-compose up -d || echo "Docker services may already be running"

# Wait for services to start
sleep 3

# Start SDN Controller in background
echo "Starting SDN Controller..."
case $ARCHITECTURE in
    centralized)
        ryu-manager sdn_controller/ryu_apps/centralized_controller.py > results/logs/controller.log 2>&1 &
        ;;
    distributed_no_ai)
        ryu-manager sdn_controller/ryu_apps/distributed_controller.py > results/logs/controller.log 2>&1 &
        ;;
    distributed_ai)
        ryu-manager sdn_controller/ryu_apps/ai_routing_app.py > results/logs/controller.log 2>&1 &
        ;;
esac

CONTROLLER_PID=$!
echo "SDN Controller started with PID: $CONTROLLER_PID"

# Wait for controller to initialize
sleep 5

# Start network topology in background
echo "Starting network topology..."
python3 fogbed/topology.py > results/logs/topology.log 2>&1 &
TOPOLOGY_PID=$!
echo "Network topology started with PID: $TOPOLOGY_PID"

# Wait for topology to initialize
sleep 5

# Start traffic generator in background
echo "Starting IoT traffic generator..."
python3 iot/traffic_generator.py --pattern periodic --devices 10 --duration 300 > results/logs/traffic.log 2>&1 &
TRAFFIC_PID=$!
echo "Traffic generator started with PID: $TRAFFIC_PID"

echo ""
echo "=== System Started ==="
echo "Architecture: $ARCHITECTURE"
echo "SDN Controller PID: $CONTROLLER_PID"
echo "Topology PID: $TOPOLOGY_PID"
echo "Traffic Generator PID: $TRAFFIC_PID"
echo ""
echo "View logs:"
echo "  Controller: tail -f results/logs/controller.log"
echo "  Topology: tail -f results/logs/topology.log"
echo "  Traffic: tail -f results/logs/traffic.log"
echo ""
echo "Monitoring:"
echo "  Prometheus: http://localhost:9090"
echo "  Grafana: http://localhost:3000 (admin/admin)"
echo ""
echo "To stop, run: sudo bash scripts/stop.sh"

# Save PIDs for stop script
echo "$CONTROLLER_PID" > /tmp/fog_controller.pid
echo "$TOPOLOGY_PID" > /tmp/fog_topology.pid
echo "$TRAFFIC_PID" > /tmp/fog_traffic.pid

