import cv2
import os
import psycopg2
import torch
from datetime import datetime
from dotenv import load_dotenv
from ultralytics import YOLO
import time

# ==============================
# Load ENV
# ==============================
load_dotenv()

DB_USER = os.getenv("USER")
DB_PASSWORD = os.getenv("PASSWORD")
DB_HOST = os.getenv("HOST")
DB_PORT = os.getenv("PORT")
DB_NAME = os.getenv("DBNAME")

# ==============================
# Supabase Connection
# ==============================
def connect_to_supabase():
    return psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        connect_timeout=5
    )

# ==============================
# Load YOLOv8 (.pt)
# ==============================
device = "cuda" if torch.cuda.is_available() else "cpu"

model = YOLO("./models/yolo11s.pt")
model.to(device)
model.eval()

print(f"[YOLO] Model loaded on {device}")

# ==============================
# Prediction (Crowd Count)
# ==============================
def predict_count(frame, conf=0.5, iou=0.5, draw=False):
    """
    frame: numpy image (BGR)
    draw: True jika ingin bounding box digambar
    """
    results = model(frame, conf=conf, iou=iou, verbose=False)
    detections = results[0].boxes

    count_person = 0

    for box in detections:
        cls_id = int(box.cls[0])  # 0 = person
        if cls_id == 0:
            count_person += 1

            if draw:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    "Person",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

    return count_person, frame

# ==============================
# Save Result to Supabase
# ==============================
def save_to_supabase(count_value, timestamp=None):
    if timestamp is None:
        timestamp = int(time.time())  # epoch seconds

    try:
        conn = connect_to_supabase()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO crowd_logs (count, timestamp)
            VALUES (%s, %s)
            """,
            (float(count_value), int(timestamp))
        )

        conn.commit()
        cur.close()
        conn.close()

        print(f"[SUPABASE] Insert OK | count={count_value:.2f}, ts={timestamp}")

    except Exception as e:
        print("[SUPABASE] ERROR:", e)


# ==============================
# Example Usage (for testing)
# ==============================
if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Camera not accessible")
        exit()

    ret, frame = cap.read()
    cap.release()

    if ret:
        count = predict_count(frame)
        print(f"[PREDICTION] Crowd count: {count}")
        save_to_supabase(count)
    else:
        print("❌ Failed to read frame")
