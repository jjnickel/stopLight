import asyncio
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np
from ultralytics import YOLO
from loguru import logger

class VehicleDetector:
    def __init__(self, model_path: Optional[Path] = None):
        """Initialize the vehicle detector with YOLOv8 model."""
        self.model = YOLO('yolov8n.pt')  # Load the smallest YOLOv8 model
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_running = False
        self.detection_interval = 0.1  # seconds
        self.confidence_threshold = 0.5
        
        # Vehicle classes in COCO dataset
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
    
    async def start(self, camera_id: int = 0):
        """Start the video capture and detection loop."""
        self.cap = cv2.VideoCapture(camera_id)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera {camera_id}")
        
        self.is_running = True
        asyncio.create_task(self._detection_loop())
        logger.info("Vehicle detector started")
    
    async def stop(self):
        """Stop the video capture and detection loop."""
        self.is_running = False
        if self.cap:
            self.cap.release()
        logger.info("Vehicle detector stopped")
    
    async def _detection_loop(self):
        """Main detection loop that processes frames and detects vehicles."""
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    logger.error("Failed to read frame from camera")
                    continue
                
                # Run detection
                results = self.model(frame, conf=self.confidence_threshold)
                
                # Process detections
                detections = self._process_detections(results[0])
                
                # TODO: Send detections to traffic analyzer
                
                await asyncio.sleep(self.detection_interval)
                
            except Exception as e:
                logger.error(f"Error in detection loop: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    def _process_detections(self, result) -> List[Dict]:
        """Process YOLO detections and extract relevant information."""
        detections = []
        
        for box in result.boxes:
            cls = int(box.cls[0])
            if cls in self.vehicle_classes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                
                detections.append({
                    'class': self.vehicle_classes[cls],
                    'confidence': confidence,
                    'bbox': (x1, y1, x2, y2)
                })
        
        return detections
    
    def get_queue_length(self, detections: List[Dict]) -> int:
        """Estimate queue length based on vehicle detections."""
        # TODO: Implement queue length estimation logic
        return len(detections)
    
    def get_traffic_density(self, detections: List[Dict], frame_area: float) -> float:
        """Calculate traffic density based on vehicle detections."""
        if not detections:
            return 0.0
        
        total_vehicle_area = sum(
            (d['bbox'][2] - d['bbox'][0]) * (d['bbox'][3] - d['bbox'][1])
            for d in detections
        )
        
        return total_vehicle_area / frame_area 