
# run.py

import cv2
import os
import time
from app.camera_handler import CameraHandler
from app.yolo_detector import YOLODetector
from app.vehicle_processor import VehicleProcessor
from app.traffic_light_controller import TrafficLightController
from app import state
from app.db.violation_logger import log_violation

# --- Init system modules ---
camera = CameraHandler(source=0)
frame_width, frame_height = 640, 480

detector = YOLODetector()
processor = VehicleProcessor(frame_width, frame_height)
controller = TrafficLightController()

# --- Violation logic config ---
stop_line_y = frame_height // 2 - 50  # define "stop line" position
violation_triggered = set()  # track IDs of objects already logged

# --- Main loop ---
while True:
    frame = camera.get_frame()
    if frame is None:
        break

    frame = cv2.resize(frame, (frame_width, frame_height))
    detections = detector.detect(frame)
    state.system_status["last_yolo_heartbeat"] = time.time()
    lane_counts = processor.count_vehicles_per_lane(detections)


    # Update shared state
    state.lane_counts.update(lane_counts)

    # Update traffic light logic
    active_lane, signal_state = controller.update_light(lane_counts)

    # --- Draw overlays ---
    for d in detections:
        x1, y1, x2, y2 = map(int, d['bbox'])
        label = f"{d['class']} ({d['conf']:.2f})"
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 8), cv2.FONT_HERSHEY_DUPLEX, 0.5, (0, 255, 0), 1)

        # --- Red Light Violation Detection ---
        center_y = (y1 + y2) // 2
        if signal_state == "RED" and center_y > stop_line_y:
            obj_id = f"{x1}_{y1}_{x2}_{y2}"
            if obj_id not in violation_triggered:
                log_violation(intersection_id=1, lane="unknown", cap=camera.cap)
                violation_triggered.add(obj_id)

    # --- Draw stop line ---
    cv2.line(frame, (0, stop_line_y), (frame_width, stop_line_y), (0, 0, 255), 2)

    # --- Draw lane counts ---
    overlay_y = 30
    for lane, count in lane_counts.items():
        text = f"{lane.capitalize()}: {count}"
        cv2.putText(frame, text, (10, overlay_y), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2)
        overlay_y += 30

    if active_lane:
        cv2.putText(frame, f"GREEN LIGHT: {active_lane.upper()}", (10, overlay_y + 10),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
    else:
        cv2.putText(frame, "WAITING FOR INITIAL GREEN", (10, overlay_y + 10),
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 2)
        
        # --- Display current AI mode (AI or FAILSAFE) ---
    cv2.putText(frame, f"MODE: {state.system_status['mode']}", (frame_width - 200, 30),
                cv2.FONT_HERSHEY_DUPLEX, 0.6,
                (0, 255, 0) if state.system_status["mode"] == "AI" else (0, 0, 255),
                2)

    # --- Display frame ---
    cv2.imshow("AI Detection Preview", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
camera.release()
cv2.destroyAllWindows()
