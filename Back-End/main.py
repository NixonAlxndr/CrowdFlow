from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, File
from prediction_worker import model, preprocess, save_to_supabase, connect_to_supabase
import numpy as np
import cv2
import time

app = FastAPI()

# Izinkan origin mana saja (untuk testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ganti "*" dengan domain tertentu kalau mau
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "running"}

# ----- Pydantic model untuk request body -----
class CrowdRecord(BaseModel):
    count: int
    timestamp: int   # epoch time (detik)

def extract_count(pred):
    while isinstance(pred, list):
        pred = pred[0]
    return float(pred)

@app.post("/upload_frame")
async def upload_frame(file: UploadFile = File(...)):
    # Baca file menjadi bytes
    contents = await file.read()

    # Decode ke numpy (OpenCV)
    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "invalid image"}

    # Preprocess → predict
    x = preprocess(frame)
    pred = model.predict(x)[0].tolist()

    # Ambil count
    count_value = extract_count(pred)
    timestamp = int(time.time())

    # Simpan ke Supabase
    save_to_supabase(count_value, timestamp)

    return {
        "count": count_value,
        "timestamp": timestamp
    }
    
@app.get("/crowd_logs")
def get_crowd_logs():
    conn = connect_to_supabase()
    cur = conn.cursor()

    query = """
        SELECT timestamp, count 
        FROM crowd_logs 
        ORDER BY timestamp ASC;
    """

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # Convert ke JSON-ready format
    data = [
        {"timestamp": r[0], "count": float(r[1])} 
        for r in rows
    ]

    return data