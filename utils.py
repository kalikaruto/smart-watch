
import cv2
import numpy as np

def add_text(frame, text):
    """Adds text to the top-left corner of a frame."""
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(frame, text, (10, 30), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
    return frame

def arrange_frames(frames, frame_size=(320, 240), cams=[]):
    """Arrange frames in a grid, showing a placeholder for offline streams."""
    num_frames = len(cams) # Base the grid on the number of cameras
    cols = int(np.ceil(np.sqrt(num_frames)))
    rows = int(np.ceil(num_frames / cols))
    
    grid_h = rows * frame_size[1]
    grid_w = cols * frame_size[0]
    blank_image = np.zeros((grid_h, grid_w, 3), dtype=np.uint8)

    for idx, cam in enumerate(cams):
        frame = frames.get(cam.get('name'))
        
        if frame is None:
            # Create a black placeholder with "Stream Offline"
            frame = np.zeros((frame_size[1], frame_size[0], 3), dtype=np.uint8)
            text = "Stream Offline"
            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(text, font, 0.5, 1)[0]
            text_x = (frame_size[0] - text_size[0]) // 2
            text_y = (frame_size[1] + text_size[1]) // 2
            cv2.putText(frame, text, (text_x, text_y), font, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

        resized_frame = cv2.resize(frame, frame_size)
        labeled_frame = add_text(resized_frame, f"{cam.get('name', 'Cam Undefined')}")

        row, col = divmod(idx, cols)
        y_start, y_end = row * frame_size[1], (row + 1) * frame_size[1]
        x_start, x_end = col * frame_size[0], (col + 1) * frame_size[0]
        blank_image[y_start:y_end, x_start:x_end] = labeled_frame

    return blank_image
