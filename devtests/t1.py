import cv2
import numpy as np

def detect_human_with_mobilenet(frame, net, confidence_threshold=0.5):
    """
    Detect humans in a frame using MobileNet-SSD.
    
    Args:
        frame (numpy.ndarray): The input frame.
        net (cv2.dnn_Net): The preloaded MobileNet-SSD model.
        confidence_threshold (float): Minimum confidence to consider a detection valid.
    
    Returns:
        bool: True if a human is detected, False otherwise.
    """
    # Preprocess the frame for the model
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    # Loop through detections
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > confidence_threshold:
            class_id = int(detections[0, 0, i, 1])
            # Class ID 15 corresponds to 'person' in MobileNet-SSD
            if class_id == 15:
                box = detections[0, 0, i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
                (x1, y1, x2, y2) = box.astype("int")
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                label = f"Person: {confidence:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                return True
    return False

# Load the MobileNet-SSD model
def load_mobilenet_model():
    """
    Load the MobileNet-SSD model.
    
    Returns:
        cv2.dnn_Net: The loaded model.
    """
    prototxt_path = "MobileNetSSD_deploy.prototxt"
    model_path = "MobileNetSSD_deploy.caffemodel"
    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    return net

# Example usage
if __name__ == "__main__":
    net = load_mobilenet_model()
    cap = cv2.VideoCapture(0)  # Use webcam for testing

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        human_detected = detect_human_with_mobilenet(frame, net)
        if human_detected:
            print("Human detected!")

        cv2.imshow("Frame", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()