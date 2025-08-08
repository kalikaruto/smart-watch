import cv2

url1 = "rtsp://admin:offset_1234@192.168.1.240:554/cam/realmonitor?channel=4&subtype=0"
cap1 = cv2.VideoCapture(url1, cv2.CAP_FFMPEG)

url2 = "rtsp://admin:offset_1234@192.168.1.240:554/cam/realmonitor?channel=2&subtype=0"
cap2 = cv2.VideoCapture(url2, cv2.CAP_FFMPEG)
url3 = "rtsp://admin:offset_1234@192.168.1.240:554/cam/realmonitor?channel=8&subtype=0"
cap3 = cv2.VideoCapture(url3, cv2.CAP_FFMPEG)

caps = [cap1, cap2, cap3]

while True:
    for idx, cap in enumerate(caps):
        ret, frame = cap.read()

        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow(f"Camera {idx+1}", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()