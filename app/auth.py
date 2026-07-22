import time
from app.config import Settings

settings = Settings()
current_time = time.time()

ACTIVE_KEYS = {} # Memory-based storage for the monolith

def validate_key(key):
    # Replace with your actual secure key validation logic
    if key != settings.X_PRIVATE_API_KEY: return False
    current_time = time.time()
    if key not in ACTIVE_KEYS:
        ACTIVE_KEYS[key] = current_time
        return True
    # Check 30 mins (1800s)
    if (current_time - ACTIVE_KEYS[key]) > 1800:
        del ACTIVE_KEYS[key]
        return False
    return True
