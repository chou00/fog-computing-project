"""
IoT Traffic Generator
Generates various traffic patterns for testing
"""

import time
import random
import threading
from typing import List, Callable
from loguru import logger
from .mqtt_client import IoTDevice


class TrafficGenerator:
    """Generates IoT traffic with different patterns"""
    
    def __init__(self, num_devices: int = 20, broker_host: str = 'localhost'):
        """
        Initialize traffic generator
        
        Args:
            num_devices: Number of IoT devices
            broker_host: MQTT broker hostname
        """
        self.num_devices = num_devices
        self.broker_host = broker_host
        self.devices: List[IoTDevice] = []
        self.is_running = False
        self.threads: List[threading.Thread] = []
        
        logger.info(f"Traffic Generator initialized with {num_devices} devices")
    
    def create_devices(self):
        """Create IoT devices"""
        for i in range(1, self.num_devices + 1):
            device = IoTDevice(
                device_id=f'iot{i}',
                device_type='sensor',
                broker_host=self.broker_host
            )
            self.devices.append(device)
    
    def start_periodic_traffic(self, interval: float = 5.0):
        """
        Start periodic traffic pattern
        
        Args:
            interval: Time interval between messages (seconds)
        """
        logger.info(f"Starting periodic traffic (interval: {interval}s)")
        
        self.create_devices()
        self.is_running = True
        
        for device in self.devices:
            device.start()
            time.sleep(0.1)  # Stagger device starts
        
        # Start periodic publishing
        for device in self.devices:
            thread = threading.Thread(
                target=self._periodic_publish,
                args=(device, interval),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
    
    def start_burst_traffic(self, burst_size: int = 100, burst_interval: float = 30.0):
        """
        Start burst traffic pattern
        
        Args:
            burst_size: Number of messages per burst
            burst_interval: Time between bursts (seconds)
        """
        logger.info(f"Starting burst traffic (burst_size: {burst_size}, interval: {burst_interval}s)")
        
        self.create_devices()
        self.is_running = True
        
        for device in self.devices:
            device.start()
        
        # Start burst publishing
        for device in self.devices:
            thread = threading.Thread(
                target=self._burst_publish,
                args=(device, burst_size, burst_interval),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
    
    def start_variable_traffic(self, min_interval: float = 1.0, max_interval: float = 10.0):
        """
        Start variable traffic pattern
        
        Args:
            min_interval: Minimum interval between messages
            max_interval: Maximum interval between messages
        """
        logger.info(f"Starting variable traffic (interval: {min_interval}-{max_interval}s)")
        
        self.create_devices()
        self.is_running = True
        
        for device in self.devices:
            device.start()
        
        # Start variable publishing
        for device in self.devices:
            thread = threading.Thread(
                target=self._variable_publish,
                args=(device, min_interval, max_interval),
                daemon=True
            )
            thread.start()
            self.threads.append(thread)
    
    def inject_anomaly(self, duration: float = 60.0, intensity: float = 10.0):
        """
        Inject anomalous traffic (e.g., DDoS-like)
        
        Args:
            duration: Duration of anomaly (seconds)
            intensity: Traffic intensity multiplier
        """
        logger.warning(f"Injecting anomaly traffic (duration: {duration}s, intensity: {intensity}x)")
        
        end_time = time.time() + duration
        
        while time.time() < end_time and self.is_running:
            # Rapid fire messages from all devices
            for device in self.devices:
                device.publish_data()
            time.sleep(0.1 / intensity)  # Very short interval
    
    def _periodic_publish(self, device: IoTDevice, interval: float):
        """Periodic publishing thread"""
        while self.is_running:
            device.publish_data()
            time.sleep(interval)
    
    def _burst_publish(self, device: IoTDevice, burst_size: int, burst_interval: float):
        """Burst publishing thread"""
        while self.is_running:
            # Send burst
            for _ in range(burst_size):
                device.publish_data()
                time.sleep(0.01)  # Small delay within burst
            
            # Wait for next burst
            time.sleep(burst_interval)
    
    def _variable_publish(self, device: IoTDevice, min_interval: float, max_interval: float):
        """Variable publishing thread"""
        while self.is_running:
            device.publish_data()
            interval = random.uniform(min_interval, max_interval)
            time.sleep(interval)
    
    def stop(self):
        """Stop traffic generation"""
        self.is_running = False
        
        for device in self.devices:
            device.stop()
        
        logger.info("Traffic generation stopped")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='IoT Traffic Generator')
    parser.add_argument('--pattern', type=str, default='periodic',
                       choices=['periodic', 'burst', 'variable', 'anomaly'],
                       help='Traffic pattern')
    parser.add_argument('--devices', type=int, default=20, help='Number of devices')
    parser.add_argument('--duration', type=int, default=300, help='Duration in seconds')
    
    args = parser.parse_args()
    
    generator = TrafficGenerator(num_devices=args.devices)
    
    try:
        if args.pattern == 'periodic':
            generator.start_periodic_traffic(interval=5.0)
        elif args.pattern == 'burst':
            generator.start_burst_traffic(burst_size=100, burst_interval=30.0)
        elif args.pattern == 'variable':
            generator.start_variable_traffic(min_interval=1.0, max_interval=10.0)
        elif args.pattern == 'anomaly':
            generator.create_devices()
            for device in generator.devices:
                device.start()
            generator.inject_anomaly(duration=args.duration, intensity=10.0)
        
        # Keep running
        time.sleep(args.duration)
    
    except KeyboardInterrupt:
        logger.info("Stopping traffic generator...")
    finally:
        generator.stop()

