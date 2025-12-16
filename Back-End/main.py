from fastapi import FastAPI, UploadFile, File, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import time
import io
import csv

from prediction_worker import (
    predict_count,
    save_to_supabase,
    connect_to_supabase
)

app = FastAPI()

# ==============================
# CORS (dev-friendly)
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# Health Check
# ==============================
@app.get("/")
def home():
    return {"status": "running"}

# ==============================
# Upload Frame → Predict → Save
# ==============================
@app.post("/upload_frame")
async def upload_frame(file: UploadFile = File(...)):
    contents = await file.read()

    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "invalid image"}

    # 🔥 YOLOv8 prediction
    count_value = predict_count(frame)
    timestamp = int(time.time())

    save_to_supabase(count_value)

    return {
        "count": count_value,
        "timestamp": timestamp
    }

# ==============================
# Crowd Logs (Graph)
# ==============================
@app.get("/crowd_logs")
def get_crowd_logs(granularity: str = Query("5sec")):
    conn = connect_to_supabase()
    cur = conn.cursor()

    if granularity == "5sec":
        query = """
        SELECT
            to_timestamp(timestamp)::timestamp(0) AS t,
            avg(count)::float AS value
        FROM crowd_logs
        GROUP BY t
        ORDER BY t DESC
        LIMIT 100;
        """

    elif granularity == "hour":
        query = """
        SELECT
            date_trunc('hour', to_timestamp(timestamp)) AS t,
            avg(count)::float AS value
        FROM crowd_logs
        GROUP BY t
        ORDER BY t;
        """

    elif granularity == "day":
        query = """
        SELECT
            date_trunc('day', to_timestamp(timestamp)) AS t,
            avg(count)::float AS value
        FROM crowd_logs
        GROUP BY t
        ORDER BY t;
        """

    elif granularity == "week":
        query = """
        SELECT
            date_trunc('week', to_timestamp(timestamp)) AS t,
            avg(count)::float AS value
        FROM crowd_logs
        GROUP BY t
        ORDER BY t;
        """

    elif granularity == "month":
        query = """
        SELECT
            date_trunc('month', to_timestamp(timestamp)) AS t,
            avg(count)::float AS value
        FROM crowd_logs
        GROUP BY t
        ORDER BY t;
        """
    else:
        return {"error": "invalid granularity"}

    cur.execute(query)
    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "time": r[0].isoformat(),
            "value": float(r[1])
        }
        for r in rows
    ]

# ==============================
# Summary Card
# ==============================
@app.get("/summary")
def get_summary():
    conn = connect_to_supabase()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            (SELECT COALESCE(AVG(count), 0)
             FROM crowd_logs
             WHERE timestamp >= EXTRACT(EPOCH FROM NOW()) - 30),

            (SELECT COALESCE(MAX(count), 0)
             FROM crowd_logs
             WHERE timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))),

            (SELECT COALESCE(AVG(count), 0)
             FROM crowd_logs
             WHERE timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))),

            (SELECT COALESCE(SUM(count), 0)
             FROM crowd_logs
             WHERE timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW())))
    """)

    row = cur.fetchone()
    cur.close()
    conn.close()

    return {
        "last_30_sec": float(row[0]),
        "peak_today": float(row[1]),
        "avg_per_hour": float(row[2]),
        "total_today": float(row[3]),
    }

# ==============================
# Export CSV
# ==============================
@app.get("/export_csv")
def export_csv():
    conn = connect_to_supabase()
    cur = conn.cursor()

    cur.execute("""
        SELECT timestamp, count
        FROM crowd_logs
        ORDER BY timestamp ASC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["time", "count"])

    for ts, count in rows:
        writer.writerow([
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)),
            float(count)
        ])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=crowd_logs.csv"
        }
    )
