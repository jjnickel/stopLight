import asyncio
import json
from typing import Callable, Dict, Optional

import paho.mqtt.client as mqtt
from loguru import logger

class MQTTClient:
    def __init__(self, broker: str = "localhost", port: int = 1883):
        """Initialize the MQTT client."""
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.is_connected = False
        
        # Set up callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle connection callback."""
        if rc == 0:
            self.is_connected = True
            logger.info("Connected to MQTT broker")
            
            # Subscribe to topics
            self.client.subscribe("traffic/+/metrics")
            self.client.subscribe("traffic/+/state")
            self.client.subscribe("traffic/+/emergency")
        else:
            logger.error(f"Failed to connect to MQTT broker with code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle disconnection callback."""
        self.is_connected = False
        logger.info("Disconnected from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming messages."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            
            # Call appropriate handler if registered
            if topic in self.message_handlers:
                self.message_handlers[topic](payload)
            else:
                logger.debug(f"Received message on topic {topic}: {payload}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    async def connect(self):
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the MQTT broker."""
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except Exception as e:
            logger.error(f"Error disconnecting from MQTT broker: {e}")
    
    def publish_metrics(self, intersection_id: str, metrics: Dict):
        """Publish traffic metrics."""
        try:
            topic = f"traffic/{intersection_id}/metrics"
            self.client.publish(topic, json.dumps(metrics))
        except Exception as e:
            logger.error(f"Failed to publish metrics: {e}")
    
    def publish_state(self, intersection_id: str, state: Dict):
        """Publish traffic light state."""
        try:
            topic = f"traffic/{intersection_id}/state"
            self.client.publish(topic, json.dumps(state))
        except Exception as e:
            logger.error(f"Failed to publish state: {e}")
    
    def publish_emergency(self, intersection_id: str, emergency: bool):
        """Publish emergency status."""
        try:
            topic = f"traffic/{intersection_id}/emergency"
            self.client.publish(topic, json.dumps({"emergency": emergency}))
        except Exception as e:
            logger.error(f"Failed to publish emergency status: {e}")
    
    def register_handler(self, topic: str, handler: Callable):
        """Register a message handler for a specific topic."""
        self.message_handlers[topic] = handler
        logger.info(f"Registered handler for topic: {topic}")
    
    def unregister_handler(self, topic: str):
        """Unregister a message handler."""
        if topic in self.message_handlers:
            del self.message_handlers[topic]
            logger.info(f"Unregistered handler for topic: {topic}") 