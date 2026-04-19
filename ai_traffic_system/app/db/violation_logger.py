
# db/violation_logger.py

import os
import cv2
import uuid
import time
from datetime import datetime
from .db_manager import log_incident

LOG_DIR = "logs"

def create_incident_folder():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    incident_id = str(uuid.uuid4())[:8]
    folder_path = os.path.join(LOG_DIR, f"incident_{incident_id}")
    os.makedirs(folder_path)
    return folder_path, incident_id

def burst_capture(cap, save_path, burst_count=5, interval=0.2):
    """
    Takes 'burst_count' frames from cap and saves them to save_path
    """
    for i in range(burst_count):
        ret, frame = cap.read()
        if not ret:
            continue
        filename = os.path.join(save_path, f"frame_{i + 1}.jpg")
        cv2.imwrite(filename, frame)
        time.sleep(interval)

def log_violation(intersection_id, lane, cap):
    folder, incident_id = create_incident_folder()
    burst_capture(cap, folder)
    log_incident(intersection_id, "red_light_violation", lane, folder)
    print(f"[LOGGED] Red light violation captured: {incident_id}")
