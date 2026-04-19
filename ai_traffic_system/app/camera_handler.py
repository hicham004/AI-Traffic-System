# app/camera_handler.py

import cv2

class CameraHandler:
    def __init__(self, source=0):
        """
        :param source: camera index (0 = default webcam) or video file path
        """
        self.source = source
        self.cap = cv2.VideoCapture(source)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {source}")

    def get_frame(self):
        """
        Reads the next frame from the camera or video.
        :return: The frame (numpy ndarray), or None if end of stream
        """
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        """
        Releases the video capture device.
        """
        self.cap.release()
