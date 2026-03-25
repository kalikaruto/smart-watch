import cv2
import time
import threading
import logging
from logger import setup_logging
from queue import Queue, Empty

class VideoStream:
    """
    A threaded video stream reader.
    This class reads frames from a camera in a dedicated thread to avoid
    blocking the main application.
    """
    def __init__(self, camera_info, max_retries=5, retry_delay=2):
        self.camera_info = camera_info
        self.link = self._get_link()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        self.cap = None
        self.queue = Queue(maxsize=2)  # Buffer only 2 frames to keep it recent
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.running = False

    def _get_link(self):
        link = self.camera_info.get('link')
        if isinstance(link, str) and link.isdigit():
            return int(link)
        return link

    def _connect(self):
        """Attempt to connect to the camera with retries."""
        for attempt in range(self.max_retries):
            if isinstance(self.link, int):
                self.cap = cv2.VideoCapture(self.link, cv2.CAP_V4L2)
            else:
                self.cap = cv2.VideoCapture(self.link, cv2.CAP_FFMPEG)
            
            if self.cap and self.cap.isOpened():
                logging.info(f"Successfully connected to camera: {self.camera_info.get('name')}")
                return True
            
            logging.warning(f"Error: Could not open camera {self.camera_info.get('name')}. Retrying ({attempt + 1}/{self.max_retries})...")
            time.sleep(self.retry_delay)
        
        logging.error(f"Failed to connect to camera: {self.camera_info.get('name')} after {self.max_retries} attempts.")
        return False

    def _run(self):
        """The main loop for the video capture thread."""
        if not self._connect():
            self.running = False
            return

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                logging.warning(f"Lost connection to {self.camera_info.get('name')}. Reconnecting...")
                self.cap.release()
                if not self._connect():
                    self.running = False
                    break
                continue

            if not self.queue.full():
                self.queue.put(frame)

    def start(self):
        """Start the video capture thread."""
        self.running = True
        self.thread.start()

    def read(self):
        """Read a frame from the queue without blocking."""
        try:
            return self.queue.get_nowait()
        except Empty:
            return None

    def is_running(self):
        return self.running

    def stop(self):
        """Stop the video capture thread."""
        self.running = False
        self.thread.join()
        if self.cap:
            self.cap.release()