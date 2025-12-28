"""
MQTT Client for IoT Devices
Handles IoT device communication via MQTT protocol
"""

import paho.mqtt.client as mqtt
import json
import time
import random
from typing import Callable, Optional
from loguru import logger


class IoTMQTTClient:
    """MQTT client for IoT devices"""
    
    def __init__(self, device_id: str, broker_host: str = 'localhost', 
                 broker_port: int = 1883, topics: Optional[list] = None):
        """
        Initialize MQTT client
        
        Args:
            device_id: Unique device identifier
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
            topics: List of topics to subscribe to
        """
        self.device_id = device_id
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.topics = topics or []
        self.client = None
        self.is_connected = False
        self.message_callbacks = {}
        
        logger.info(f"IoT MQTT Client initialized: device_id={device_id}")
    
    def connect(self):
        """Connect to MQTT broker"""
        self.client = mqtt.Client(client_id=self.device_id)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            logger.info(f"Connecting to MQTT broker at {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_connected = False
            logger.info(f"Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for connection"""
        if rc == 0:
            self.is_connected = True
            logger.info(f"Connected to MQTT broker")
            
            # Subscribe to topics
            for topic in self.topics:
                client.subscribe(topic)
                logger.info(f"Subscribed to topic: {topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for disconnection"""
        self.is_connected = False
        logger.info(f"Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Callback for received messages"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        logger.debug(f"Received message on topic {topic}: {payload}")
        
        # Call registered callback if exists
        if topic in self.message_callbacks:
            try:
                data = json.loads(payload)
                self.message_callbacks[topic](topic, data)
            except json.JSONDecodeError:
                self.message_callbacks[topic](topic, payload)
    
    def subscribe(self, topic: str, callback: Optional[Callable] = None):
        """
        Subscribe to a topic
        
        Args:
            topic: Topic to subscribe to
            callback: Optional callback function
        """
        if self.client and self.is_connected:
            self.client.subscribe(topic)
            if callback:
                self.message_callbacks[topic] = callback
            logger.info(f"Subscribed to topic: {topic}")
    
    def publish(self, topic: str, payload: dict, qos: int = 0):
        """
        Publish message to topic
        
        Args:
            topic: Topic to publish to
            payload: Message payload (dict)
            qos: Quality of Service level
        """
        if self.client and self.is_connected:
            message = json.dumps(payload)
            result = self.client.publish(topic, message, qos=qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {payload}")
            else:
                logger.error(f"Failed to publish to {topic}")
        else:
            logger.warning("MQTT client not connected")


class IoTDevice:
    """IoT device that generates and sends data via MQTT"""
    
    def __init__(self, device_id: str, device_type: str = 'sensor',
                 broker_host: str = 'localhost', broker_port: int = 1883):
        """
        Initialize IoT device
        
        Args:
            device_id: Unique device identifier
            device_type: Type of device ('sensor', 'actuator', etc.)
            broker_host: MQTT broker hostname
            broker_port: MQTT broker port
        """
        self.device_id = device_id
        self.device_type = device_type
        self.mqtt_client = IoTMQTTClient(
            device_id=device_id,
            broker_host=broker_host,
            broker_port=broker_port,
            topics=[f'iot/devices/{device_id}/commands']
        )
        self.is_running = False
        self.data_topic = f'iot/devices/{device_id}/data'
        self.status_topic = f'iot/devices/{device_id}/status'
        
        logger.info(f"IoT Device initialized: {device_id} ({device_type})")
    
    def start(self):
        """Start the IoT device"""
        self.mqtt_client.connect()
        time.sleep(1)  # Wait for connection
        self.is_running = True
        
        # Publish initial status
        self.publish_status('online')
        logger.info(f"IoT Device {self.device_id} started")
    
    def stop(self):
        """Stop the IoT device"""
        self.is_running = False
        self.publish_status('offline')
        self.mqtt_client.disconnect()
        logger.info(f"IoT Device {self.device_id} stopped")
    
    def generate_sensor_data(self) -> dict:
        """
        Generate sensor data
        
        Returns:
            Dictionary with sensor readings
        """
        timestamp = time.time()
        
        if self.device_type == 'sensor':
            # Simulate sensor readings
            data = {
                'device_id': self.device_id,
                'timestamp': timestamp,
                'temperature': round(random.uniform(20.0, 30.0), 2),
                'humidity': round(random.uniform(40.0, 60.0), 2),
                'pressure': round(random.uniform(1000.0, 1020.0), 2)
            }
        else:
            # Generic data
            data = {
                'device_id': self.device_id,
                'timestamp': timestamp,
                'value': random.uniform(0.0, 100.0)
            }
        
        return data
    
    def publish_data(self, data: Optional[dict] = None):
        """
        Publish sensor data
        
        Args:
            data: Optional data dict, if None generates new data
        """
        if data is None:
            data = self.generate_sensor_data()
        
        self.mqtt_client.publish(self.data_topic, data, qos=1)
    
    def publish_status(self, status: str):
        """
        Publish device status
        
        Args:
            status: Status string ('online', 'offline', 'error')
        """
        status_data = {
            'device_id': self.device_id,
            'status': status,
            'timestamp': time.time()
        }
        self.mqtt_client.publish(self.status_topic, status_data, qos=1)
    
    def run_periodic(self, interval: float = 5.0):
        """
        Run device in periodic mode
        
        Args:
            interval: Time interval between data publications (seconds)
        """
        self.start()
        
        try:
            while self.is_running:
                self.publish_data()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Stopping IoT device")
        finally:
            self.stop()

