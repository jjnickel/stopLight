import asyncio
import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from loguru import logger

from ai_vision.detector import VehicleDetector
from traffic_analyzer.analyzer import TrafficAnalyzer
from signal_controller.controller import SignalController
from database.manager import DatabaseManager
from communication.mqtt_client import MQTTClient
from admin_dashboard.app import create_dashboard_app

class StoplightSystem:
    def __init__(self, config_path: Optional[Path] = None):
        self.logger = logger
        self.setup_logging()
        
        # Initialize components
        self.db = DatabaseManager()
        self.detector = VehicleDetector()
        self.analyzer = TrafficAnalyzer(self.db)
        self.controller = SignalController(self.analyzer)
        self.mqtt_client = MQTTClient()
        
        # Initialize FastAPI app
        self.app = create_dashboard_app(self)
        
    def setup_logging(self):
        """Configure logging for the application."""
        self.logger.add(
            "logs/stoplight_{time}.log",
            rotation="1 day",
            retention="7 days",
            level="INFO"
        )
    
    async def start(self):
        """Start all system components."""
        try:
            # Initialize database
            await self.db.initialize()
            
            # Start MQTT client
            await self.mqtt_client.connect()
            
            # Start AI vision processing
            await self.detector.start()
            
            # Start traffic analysis
            await self.analyzer.start()
            
            # Start signal controller
            await self.controller.start()
            
            self.logger.info("Stoplight system started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start system: {e}")
            raise
    
    async def stop(self):
        """Stop all system components gracefully."""
        try:
            await self.detector.stop()
            await self.analyzer.stop()
            await self.controller.stop()
            await self.mqtt_client.disconnect()
            await self.db.close()
            
            self.logger.info("Stoplight system stopped successfully")
            
        except Exception as e:
            self.logger.error(f"Error during system shutdown: {e}")
            raise

async def main():
    """Main entry point for the application."""
    system = StoplightSystem()
    
    try:
        await system.start()
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await system.stop()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        await system.stop()
        raise

if __name__ == "__main__":
    asyncio.run(main()) 