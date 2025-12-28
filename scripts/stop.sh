#!/bin/bash
# Stop Script for Fog Computing Project

echo "=== Stopping Fog Computing System ==="

# Stop processes by PID if files exist
if [ -f /tmp/fog_controller.pid ]; then
    CONTROLLER_PID=$(cat /tmp/fog_controller.pid)
    echo "Stopping SDN Controller (PID: $CONTROLLER_PID)..."
    kill $CONTROLLER_PID 2>/dev/null || true
    rm /tmp/fog_controller.pid
fi

if [ -f /tmp/fog_topology.pid ]; then
    TOPOLOGY_PID=$(cat /tmp/fog_topology.pid)
    echo "Stopping Network Topology (PID: $TOPOLOGY_PID)..."
    kill $TOPOLOGY_PID 2>/dev/null || true
    rm /tmp/fog_topology.pid
fi

if [ -f /tmp/fog_traffic.pid ]; then
    TRAFFIC_PID=$(cat /tmp/fog_traffic.pid)
    echo "Stopping Traffic Generator (PID: $TRAFFIC_PID)..."
    kill $TRAFFIC_PID 2>/dev/null || true
    rm /tmp/fog_traffic.pid
fi

# Kill any remaining processes
echo "Cleaning up remaining processes..."
pkill -f ryu-manager 2>/dev/null || true
pkill -f topology.py 2>/dev/null || true
pkill -f traffic_generator.py 2>/dev/null || true
pkill -f fog_node.py 2>/dev/null || true

# Stop Docker services
echo "Stopping Docker services..."
docker-compose down 2>/dev/null || true

# Clean up Mininet
echo "Cleaning up Mininet..."
mn -c 2>/dev/null || true

echo "=== System Stopped ==="

