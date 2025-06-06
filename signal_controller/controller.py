import asyncio
from datetime import datetime
from typing import Dict, Optional

from loguru import logger
from traffic_analyzer.analyzer import TrafficAnalyzer

class SignalController:
    def __init__(self, analyzer: TrafficAnalyzer):
        """Initialize the signal controller with traffic analyzer."""
        self.analyzer = analyzer
        self.is_running = False
        self.update_interval = 1.0  # seconds
        
        # Default timing configuration
        self.timing_config = {
            'min_green': 10.0,  # seconds
            'max_green': 60.0,
            'yellow': 3.0,
            'min_red': 10.0,
            'max_red': 60.0
        }
        
        # Current state
        self.current_state = {
            'phase': 'red',  # red, yellow, green
            'remaining_time': 0.0,
            'start_time': datetime.utcnow()
        }
        
        # Emergency override
        self.emergency_override = False
    
    async def start(self):
        """Start the signal control loop."""
        self.is_running = True
        asyncio.create_task(self._control_loop())
        logger.info("Signal controller started")
    
    async def stop(self):
        """Stop the signal control loop."""
        self.is_running = False
        logger.info("Signal controller stopped")
    
    async def _control_loop(self):
        """Main control loop that manages traffic light timing."""
        while self.is_running:
            try:
                # Get current traffic metrics
                metrics = self.analyzer.get_traffic_metrics()
                
                # Calculate optimal timing
                timing = self.analyzer.calculate_optimal_timing()
                
                # Update signal timing
                await self._update_signal_timing(timing)
                
                # Check for emergency vehicles
                if self.analyzer.detect_emergency_vehicle([]):
                    await self._handle_emergency()
                
                await asyncio.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error in control loop: {e}")
                await asyncio.sleep(1)
    
    async def _update_signal_timing(self, timing: Dict[str, float]):
        """Update traffic light timing based on analysis."""
        # Ensure timing is within configured limits
        timing['green_duration'] = max(
            self.timing_config['min_green'],
            min(timing['green_duration'], self.timing_config['max_green'])
        )
        
        timing['red_duration'] = max(
            self.timing_config['min_red'],
            min(timing['red_duration'], self.timing_config['max_red'])
        )
        
        # Update current state
        self.current_state.update({
            'phase': 'green' if self.current_state['phase'] == 'red' else 'red',
            'remaining_time': timing['green_duration'] if self.current_state['phase'] == 'green' else timing['red_duration'],
            'start_time': datetime.utcnow()
        })
        
        logger.info(f"Updated signal timing: {timing}")
    
    async def _handle_emergency(self):
        """Handle emergency vehicle detection."""
        if not self.emergency_override:
            self.emergency_override = True
            # Force green light for emergency vehicle
            self.current_state.update({
                'phase': 'green',
                'remaining_time': 30.0,  # Extended green time
                'start_time': datetime.utcnow()
            })
            logger.info("Emergency vehicle detected - forcing green light")
    
    def get_current_state(self) -> Dict:
        """Get current traffic light state."""
        return self.current_state.copy()
    
    def set_timing_config(self, config: Dict[str, float]):
        """Update timing configuration."""
        self.timing_config.update(config)
        logger.info(f"Updated timing configuration: {config}")
    
    def reset_emergency_override(self):
        """Reset emergency override state."""
        self.emergency_override = False
        logger.info("Emergency override reset") 