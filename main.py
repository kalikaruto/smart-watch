import cv2
import sys
import time
import logging
from logger import setup_logging
from multiprocessing import Pool, Manager

from config import load_config, load_cameras
from video_stream import VideoStream
from detection import DetectionProcessor
from notifications import NotificationManager
from utils import arrange_frames
from cli import CameraApp

def detection_worker(config, notification_queue, frame_queue, shared_last_alert_times):
    """Worker function for the detection process pool."""
    notification_manager = NotificationManager(config)
    notification_manager.queue = notification_queue
    notification_manager.start()
    
    detector = DetectionProcessor(config, notification_manager, shared_last_alert_times)
    
    while True:
        task = frame_queue.get()
        if task is None: # Shutdown signal
            break
        
        frame, camera_info = task
        detector.process_frame(frame, camera_info)

def main(show_frames=False):
    config = load_config()
    cameras = load_cameras()

    if not cameras:
        logging.warning("No cameras configured. Launching Camera Manager CLI...")
        cli_app = CameraApp()
        cli_app.run()
        # After CLI closes, try loading cameras again
        cameras = load_cameras()
        if not cameras:
            logging.info("No cameras were added. Exiting application.")
            return

    # Create shared queues
    manager = Manager()
    frame_queue = manager.Queue(maxsize=100)
    notification_queue = manager.Queue()

    # Start video streams
    stream_retries = max(1, int(config.get('camera_max_retries', 3)))
    stream_retry_delay = max(0.1, float(config.get('camera_retry_delay', 1)))
    streams = [
        VideoStream(cam, max_retries=stream_retries, retry_delay=stream_retry_delay)
        for cam in cameras
    ]
    for stream in streams:
        stream.start()

    # Create a shared dictionary for last alert times
    shared_last_alert_times = manager.dict()

    # Start detection process pool
    cpu_based_workers = max(1, cv2.getNumberOfCPUs() - 1) # Leave one CPU for other tasks
    configured_max_workers = int(config.get('max_workers', cpu_based_workers))
    num_processes = max(1, min(cpu_based_workers, configured_max_workers))
    pool = Pool(num_processes, detection_worker, (config, notification_queue, frame_queue, shared_last_alert_times))

    logging.info(
        f"Starting detection with {num_processes} worker processes "
        f"(cpu_limit={cpu_based_workers}, configured_max={configured_max_workers})."
    )

    latest_frames = {cam.get('name'): None for cam in cameras}

    try:
        while True:
            # Read the latest frame from each stream
            for stream in streams:
                if not stream.is_running():
                    latest_frames[stream.camera_info.get('name')] = None
                    continue
                
                frame = stream.read()
                if frame is not None:
                    cam_name = stream.camera_info.get('name')
                    latest_frames[cam_name] = frame
                    frame_queue.put((frame, stream.camera_info))

            if show_frames:
                if latest_frames:
                    final_frame = arrange_frames(latest_frames, cams=cameras)
                    cv2.imshow("Trespass Detection", final_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
            
            time.sleep(0.01) # Yield to other threads

    except KeyboardInterrupt:
        logging.info("Stopping application...")
    finally:
        # Shutdown sequence
        for stream in streams:
            stream.stop()
        
        for _ in range(num_processes):
            frame_queue.put(None) # Send shutdown signal to all worker processes
        
        pool.close()
        pool.join()
        
        # The notification manager is managed by the worker processes

        cv2.destroyAllWindows()
        logging.info("Application stopped.")

if __name__ == "__main__":
    show = '--show' in sys.argv
    main(show_frames=show)