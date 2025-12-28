#!/usr/bin/env python3
"""
Simple Python launcher for Fog Computing Project
Works on both Linux and Windows (for testing components)
"""

import argparse
import sys
import os
import subprocess
import platform

def check_requirements():
    """Check if basic requirements are met"""
    print("Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        return False
    
    # Check if we're on Linux (for full functionality)
    is_linux = platform.system() == 'Linux'
    if not is_linux:
        print("WARNING: Not running on Linux. Full network emulation requires Linux.")
        print("Consider using WSL2 or a Linux VM for full functionality.")
    
    return True

def run_controller(architecture):
    """Run SDN controller"""
    print(f"Starting SDN Controller: {architecture}")
    
    controller_map = {
        'centralized': 'sdn_controller/ryu_apps/centralized_controller.py',
        'distributed_no_ai': 'sdn_controller/ryu_apps/distributed_controller.py',
        'distributed_ai': 'sdn_controller/ryu_apps/ai_routing_app.py'
    }
    
    if architecture not in controller_map:
        print(f"ERROR: Unknown architecture: {architecture}")
        return False
    
    controller_file = controller_map[architecture]
    
    if not os.path.exists(controller_file):
        print(f"ERROR: Controller file not found: {controller_file}")
        return False
    
    try:
        # Try to import ryu
        import ryu
        print("Ryu SDN framework found")
    except ImportError:
        print("ERROR: Ryu not installed. Run: pip install ryu")
        return False
    
    # Run controller
    cmd = ['ryu-manager', controller_file]
    print(f"Running: {' '.join(cmd)}")
    
    if platform.system() == 'Linux':
        # On Linux, may need sudo
        print("Note: On Linux, you may need to run with sudo")
    
    subprocess.run(cmd)
    return True

def run_topology():
    """Run network topology"""
    print("Starting network topology...")
    
    if platform.system() != 'Linux':
        print("ERROR: Network topology requires Linux (Mininet)")
        print("Use WSL2 or a Linux VM")
        return False
    
    topology_file = 'fogbed/topology.py'
    if not os.path.exists(topology_file):
        print(f"ERROR: Topology file not found: {topology_file}")
        return False
    
    cmd = ['python3', topology_file]
    print(f"Running: {' '.join(cmd)}")
    print("Note: This requires root access on Linux")
    
    subprocess.run(cmd)
    return True

def run_traffic_generator(pattern='periodic', devices=20, duration=300):
    """Run IoT traffic generator"""
    print(f"Starting traffic generator: pattern={pattern}, devices={devices}")
    
    traffic_file = 'iot/traffic_generator.py'
    if not os.path.exists(traffic_file):
        print(f"ERROR: Traffic generator not found: {traffic_file}")
        return False
    
    cmd = ['python3', traffic_file, 
            '--pattern', pattern,
            '--devices', str(devices),
            '--duration', str(duration)]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)
    return True

def run_tests(architecture, scenario='all', duration=300):
    """Run test scenarios"""
    print(f"Running tests: architecture={architecture}, scenario={scenario}")
    
    test_file = 'tests/test_scenarios.py'
    if not os.path.exists(test_file):
        print(f"ERROR: Test file not found: {test_file}")
        return False
    
    cmd = ['python3', test_file,
            '--architecture', architecture,
            '--scenario', scenario,
            '--duration', str(duration)]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)
    return True

def test_ai_models():
    """Test AI models without network"""
    print("Testing AI models...")
    
    try:
        import torch
        print("✓ PyTorch found")
    except ImportError:
        print("✗ PyTorch not found. Install: pip install torch")
        return False
    
    # Test LSTM
    print("\nTesting LSTM Load Predictor...")
    try:
        from ai_models.lstm.model import LoadPredictor
        predictor = LoadPredictor()
        print("✓ LSTM model initialized")
    except Exception as e:
        print(f"✗ LSTM error: {e}")
        return False
    
    # Test Autoencoder
    print("\nTesting Autoencoder...")
    try:
        from ai_models.autoencoder.model import AnomalyDetectionModel
        detector = AnomalyDetectionModel()
        print("✓ Autoencoder initialized")
    except Exception as e:
        print(f"✗ Autoencoder error: {e}")
        return False
    
    # Test RL Agent
    print("\nTesting RL Agent...")
    try:
        from ai_models.rl.dqn_agent import DQNAgent
        agent = DQNAgent(state_size=25, action_size=5)
        print("✓ RL Agent initialized")
    except Exception as e:
        print(f"✗ RL Agent error: {e}")
        return False
    
    print("\n✓ All AI models working!")
    return True

def main():
    parser = argparse.ArgumentParser(description='Fog Computing Project Launcher')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Controller command
    controller_parser = subparsers.add_parser('controller', help='Run SDN controller')
    controller_parser.add_argument('--architecture', type=str, required=True,
                                  choices=['centralized', 'distributed_no_ai', 'distributed_ai'],
                                  help='Architecture type')
    
    # Topology command
    topology_parser = subparsers.add_parser('topology', help='Run network topology')
    
    # Traffic command
    traffic_parser = subparsers.add_parser('traffic', help='Run traffic generator')
    traffic_parser.add_argument('--pattern', type=str, default='periodic',
                               choices=['periodic', 'burst', 'variable'],
                               help='Traffic pattern')
    traffic_parser.add_argument('--devices', type=int, default=20, help='Number of devices')
    traffic_parser.add_argument('--duration', type=int, default=300, help='Duration in seconds')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run test scenarios')
    test_parser.add_argument('--architecture', type=str, required=True,
                           choices=['centralized', 'distributed_no_ai', 'distributed_ai'],
                           help='Architecture type')
    test_parser.add_argument('--scenario', type=str, default='all',
                           choices=['baseline', 'burst', 'failure', 'all'],
                           help='Test scenario')
    test_parser.add_argument('--duration', type=int, default=300, help='Duration in seconds')
    
    # Test AI command
    subparsers.add_parser('test-ai', help='Test AI models (no network required)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Execute command
    if args.command == 'controller':
        run_controller(args.architecture)
    elif args.command == 'topology':
        run_topology()
    elif args.command == 'traffic':
        run_traffic_generator(args.pattern, args.devices, args.duration)
    elif args.command == 'test':
        run_tests(args.architecture, args.scenario, args.duration)
    elif args.command == 'test-ai':
        test_ai_models()

if __name__ == '__main__':
    main()

