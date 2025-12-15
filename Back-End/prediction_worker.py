import cv2
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
import onnxruntime as ort

load_dotenv()

# ==============================
# Supabase (PostgreSQL)
# ==============================
DB_USER = os.getenv("USER")
DB_PASSWORD = os.getenv("PASSWORD")
DB_HOST = os.getenv("HOST")
DB_PORT = os.getenv("PORT")
DB_NAME = os.getenv("DBNAME")

def connect_to_supabase():
    return psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        connect_timeout=5
    )

session = ort.InferenceSession(
    "./models/yolov8n.onnx",
    providers=["CPUExecutionProvider"]
)

input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

print("[ONNX] Input :", input_name, session.get_inputs()[0].shape)
print("[ONNX] Output:", output_name, session.get_outputs()[0].shape)

def preprocess(frame):
    img = cv2.resize(frame, (640, 640))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img.astype(np.float32) / 255.0

    # HWC -> CHW
    img = np.transpose(img, (2, 0, 1))

    return np.expand_dims(img, axis=0)

def predict_count(frame):
    x = preprocess(frame)

    output = session.run(
        [output_name],
        {input_name: x}
    )

    density_map = output[0]

    # MCNN count = sum of density map
    count = float(np.sum(density_map))
    return count

# ==============================
# Save to Supabase
# ==============================
def save_to_supabase(count_value, timestamp):
    try:
        conn = connect_to_supabase()
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO crowd_logs (count, timestamp)
            VALUES (%s, %s)
            """,
            (count_value, timestamp)
        )

        conn.commit()
        cur.close()
        conn.close()

        print(f"[SUPABASE] Insert OK | count={count_value:.2f}, ts={timestamp}")

    except Exception as e:
        print("[SUPABASE] ERROR:", e)
