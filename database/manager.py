import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import aiosqlite
from loguru import logger

class DatabaseManager:
    def __init__(self, db_path: str = "traffic_data.db"):
        """Initialize the database manager."""
        self.db_path = db_path
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def initialize(self):
        """Initialize the database and create tables."""
        try:
            self.connection = await aiosqlite.connect(self.db_path)
            
            # Create tables
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS traffic_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    vehicle_count INTEGER NOT NULL,
                    queue_length INTEGER NOT NULL,
                    traffic_density REAL NOT NULL,
                    average_wait_time REAL NOT NULL
                )
            """)
            
            await self.connection.execute("""
                CREATE TABLE IF NOT EXISTS signal_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    phase TEXT NOT NULL,
                    duration REAL NOT NULL,
                    is_emergency BOOLEAN NOT NULL
                )
            """)
            
            await self.connection.commit()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    async def close(self):
        """Close the database connection."""
        if self.connection:
            await self.connection.close()
            logger.info("Database connection closed")
    
    async def store_traffic_metrics(self, timestamp: datetime, metrics: Dict):
        """Store traffic metrics in the database."""
        try:
            await self.connection.execute("""
                INSERT INTO traffic_metrics (
                    timestamp, vehicle_count, queue_length,
                    traffic_density, average_wait_time
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                timestamp,
                metrics['vehicle_count'],
                metrics['queue_length'],
                metrics['traffic_density'],
                metrics['average_wait_time']
            ))
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to store traffic metrics: {e}")
            raise
    
    async def store_signal_state(self, timestamp: datetime, phase: str, duration: float, is_emergency: bool):
        """Store traffic light state in the database."""
        try:
            await self.connection.execute("""
                INSERT INTO signal_states (
                    timestamp, phase, duration, is_emergency
                ) VALUES (?, ?, ?, ?)
            """, (timestamp, phase, duration, is_emergency))
            
            await self.connection.commit()
            
        except Exception as e:
            logger.error(f"Failed to store signal state: {e}")
            raise
    
    async def get_historical_metrics(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Retrieve historical traffic metrics."""
        try:
            async with self.connection.execute("""
                SELECT * FROM traffic_metrics
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (start_time, end_time)) as cursor:
                rows = await cursor.fetchall()
                
                return [{
                    'timestamp': row[1],
                    'vehicle_count': row[2],
                    'queue_length': row[3],
                    'traffic_density': row[4],
                    'average_wait_time': row[5]
                } for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to retrieve historical metrics: {e}")
            raise
    
    async def get_signal_states(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Retrieve historical signal states."""
        try:
            async with self.connection.execute("""
                SELECT * FROM signal_states
                WHERE timestamp BETWEEN ? AND ?
                ORDER BY timestamp ASC
            """, (start_time, end_time)) as cursor:
                rows = await cursor.fetchall()
                
                return [{
                    'timestamp': row[1],
                    'phase': row[2],
                    'duration': row[3],
                    'is_emergency': bool(row[4])
                } for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to retrieve signal states: {e}")
            raise 