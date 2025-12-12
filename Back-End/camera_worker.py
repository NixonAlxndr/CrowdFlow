import cv2
import threading
import time

latest_frame = None

# 0 = webcam
# Untuk CCTV gunakan RTSP: "rtsp://user:pass@ip:554/stream"
CAMERA_SOURCE = 1

def camera_loop():
    global latest_frame

    cap = cv2.VideoCapture(CAMERA_SOURCE)

    while True:
        ret, frame = cap.read()
        if ret:
            latest_frame = frame
        time.sleep(0.1)  # 10 FPS cukup

def start_camera_thread():
    t = threading.Thread(target=camera_loop, daemon=True)
    t.start()
