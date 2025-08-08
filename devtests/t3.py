import cv2

cap = cv2.VideoCapture("https://192.0.0.4:8080/video")  # Use webcam for testing

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Webcam Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()