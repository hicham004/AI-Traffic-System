
# multi_cam_run.py

import cv2
import time
from threading import Thread
from app.camera_registry import camera_registry
from app.yolo_detector import YOLODetector
from app.vehicle_processor import VehicleProcessor
from app import state

# System-wide YOLO + shared processor
detector = YOLODetector()
frame_width, frame_height = 640, 480
processor = VehicleProcessor(frame_width, frame_height)

# Threaded processing per camera
def process_camera(cam):
    cap = cv2.VideoCapture(cam["source"])
    zone = cam["zone"]
    cam_id = cam["camera_id"]

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (frame_width, frame_height))
        detections = detector.detect(frame)
        count = processor.count_vehicles_in_zone(detections, zone)

        # Update global state
        state.lane_counts[zone] = count
        state.system_status["last_yolo_heartbeat"] = time.time()

        # Display feed
        cv2.putText(frame, f"{zone.upper()} ({cam_id}) - Vehicles: {count}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.imshow(f"Feed: {zone}", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyWindow(f"Feed: {zone}")

# Launch all camera threads
threads = []
for cam in camera_registry:
    t = Thread(target=process_camera, args=(cam,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

cv2.destroyAllWindows()
