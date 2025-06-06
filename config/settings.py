import os
from pathlib import Path
from typing import Dict, Any

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Create necessary directories
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Database settings
DATABASE = {
    "path": str(DATA_DIR / "traffic_data.db"),
    "pool_size": 5,
    "max_overflow": 10
}

# MQTT settings
MQTT = {
    "broker": os.getenv("MQTT_BROKER", "localhost"),
    "port": int(os.getenv("MQTT_PORT", "1883")),
    "client_id": os.getenv("MQTT_CLIENT_ID", "traffic_light_1"),
    "username": os.getenv("MQTT_USERNAME", ""),
    "password": os.getenv("MQTT_PASSWORD", "")
}

# AI Vision settings
VISION = {
    "model_path": os.getenv("YOLO_MODEL_PATH", "yolov8n.pt"),
    "confidence_threshold": 0.5,
    "detection_interval": 0.1,  # seconds
    "camera_id": int(os.getenv("CAMERA_ID", "0"))
}

# Traffic light timing settings
TIMING = {
    "min_green": 10.0,  # seconds
    "max_green": 60.0,
    "yellow": 3.0,
    "min_red": 10.0,
    "max_red": 60.0
}

# Security settings
SECURITY = {
    "secret_key": os.getenv("SECRET_KEY", "your-secret-key"),
    "algorithm": "HS256",
    "access_token_expire_minutes": 30
}

# Logging settings
LOGGING = {
    "level": os.getenv("LOG_LEVEL", "INFO"),
    "format": "{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    "rotation": "1 day",
    "retention": "7 days"
}

# Admin dashboard settings
DASHBOARD = {
    "host": os.getenv("DASHBOARD_HOST", "0.0.0.0"),
    "port": int(os.getenv("DASHBOARD_PORT", "8000")),
    "debug": os.getenv("DASHBOARD_DEBUG", "False").lower() == "true"
}

def get_settings() -> Dict[str, Any]:
    """Get all settings as a dictionary."""
    return {
        "database": DATABASE,
        "mqtt": MQTT,
        "vision": VISION,
        "timing": TIMING,
        "security": SECURITY,
        "logging": LOGGING,
        "dashboard": DASHBOARD
    } 