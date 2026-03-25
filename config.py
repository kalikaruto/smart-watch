
import json
import os
from dotenv import load_dotenv

# The absolute path to the directory containing this script
APP_DIR = os.path.dirname(os.path.abspath(__file__))

def get_absolute_path(path):
    """Constructs an absolute path from a path relative to the app directory."""
    return os.path.join(APP_DIR, path)

def load_config():
    """Loads camera configurations and environment variables using absolute paths."""
    env_path = get_absolute_path('.env')
    load_dotenv(dotenv_path=env_path)
    
    config = {
        "fps": int(os.getenv("FPS", 5)),
        "check_period": int(os.getenv("CHECK_PERIOD", 5)),
        "notification_cooldown": int(os.getenv("NOTIFICATION_COOLDOWN", 180)),
        "sender_email": os.getenv("SENDER_EMAIL"),
        "receiver_email": os.getenv("RECEIVER_EMAIL"),
        "sender_pass": os.getenv("SENDER_PASS"),
        "telegram_token": os.getenv("TELEGRAM_TOKEN"),
        "telegram_chat_id": os.getenv("TELEGRAM_CHAT_ID"),
        "model_path": get_absolute_path(os.getenv("MODEL_PATH", "models/MobileNetSSD_deploy.caffemodel")),
        "prototxt_path": get_absolute_path(os.getenv("PROTOTXT_PATH", "models/MobileNetSSD_deploy.prototxt")),
        "confidence_threshold": float(os.getenv("CONFIDENCE_THRESHOLD", 0.5))
    }
    
    return config

def load_cameras(filepath="data.json"):
    """Loads camera data from a JSON file using an absolute path."""
    abs_filepath = get_absolute_path(filepath)
    if not os.path.exists(abs_filepath):
        return []
    try:
        with open(abs_filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_cameras(data, filepath="data.json"):
    """Saves camera data to a JSON file using an absolute path."""
    abs_filepath = get_absolute_path(filepath)
    with open(abs_filepath, 'w') as f:
        json.dump(data, f, indent=4)

