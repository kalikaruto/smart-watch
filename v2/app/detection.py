import cv2
import numpy as np
import logging
from logger import setup_logging
from datetime import datetime
import time
import os

class DetectionProcessor:
    """
    Handles motion and human detection in a separate process.
    """
    def __init__(self, config, notification_manager, shared_last_alert_times):
        self.config = config
        self.notification_manager = notification_manager
        self.net = self._load_model()
        self.backSub = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=16, detectShadows=False)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        self.last_alert_times = shared_last_alert_times

    def _load_model(self):
        if not os.path.isfile(self.config['prototxt_path']):
            raise FileNotFoundError(f"Prototxt file not found: {self.config['prototxt_path']}")
        if not os.path.isfile(self.config['model_path']):
            raise FileNotFoundError(f"Model file not found: {self.config['model_path']}")
        return cv2.dnn.readNetFromCaffe(self.config['prototxt_path'], self.config['model_path'])

    def process_frame(self, frame, camera_info):
        """Process a single frame for motion and human detection."""
        cam_name = camera_info.get('name')
        if self._detect_motion(frame):
            logging.info(f"Motion detected in {cam_name}")
            if self._detect_human(frame):
                logging.info(f"Human detected in {cam_name}")
                if self._should_send_alert(cam_name):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logging.info(f"Sending alert for {cam_name} at {timestamp}")
                    # self.notification_manager.queue_notification(timestamp, camera_info, frame)
                    self.last_alert_times[cam_name] = time.time()

    def _detect_motion(self, frame):
        """Detects motion in a frame."""
        fgMask = self.backSub.apply(frame)
        fgMask = cv2.morphologyEx(fgMask, cv2.MORPH_OPEN, self.kernel)
        contours, _ = cv2.findContours(fgMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            if 1000 < cv2.contourArea(contour) < 10000:
                return True
        return False

    def _detect_human(self, frame):
        """Detects humans in a frame."""
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > self.config['confidence_threshold']:
                class_id = int(detections[0, 0, i, 1])
                if class_id == 15: # 15 is the class ID for 'person'
                    return True
        return False

    def _should_send_alert(self, cam_name):
        """Checks if an alert should be sent based on the cooldown."""
        last_alert_time = self.last_alert_times.get(cam_name, 0)
        return (time.time() - last_alert_time) > self.config['notification_cooldown']
