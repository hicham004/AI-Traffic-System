# app/yolo_detector.py

from ultralytics import YOLO
import numpy as np

class YOLODetector:
    def __init__(self, model_path="models/yolov8n.pt", conf_threshold=0.4):
        """
        Loads the YOLOv8 model.
        :param model_path: Path to the YOLOv8 model
        :param conf_threshold: Minimum confidence for detections
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold

        # Only detect classes of interest (e.g., cars, trucks, buses, motorcycles)
        self.target_classes = [2, 3, 5, 7]  # vehicle class IDs in COCO

    def detect(self, frame):
        """
        Runs object detection on a frame.
        :param frame: Image as numpy ndarray
        :return: List of detections → [{'class': name, 'conf': float, 'bbox': [x1, y1, x2, y2]}]
        """
        results = self.model.predict(source=frame, conf=self.conf_threshold, classes=self.target_classes, verbose=False)
        detections = []

        for r in results:
            boxes = r.boxes
            for i in range(len(boxes.cls)):
                cls_id = int(boxes.cls[i].item())
                conf = float(boxes.conf[i].item())
                xyxy = boxes.xyxy[i].tolist()
                detections.append({
                    'class': self.model.names[cls_id],
                    'conf': conf,
                    'bbox': xyxy
                })
        return detections
