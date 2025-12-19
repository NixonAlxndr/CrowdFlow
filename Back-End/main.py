from fastapi import FastAPI, UploadFile, File, Query, Response
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import cv2
import time
import io
import csv
from datetime import datetime
import pytz

from prediction_worker import (
    predict_count,
    save_to_supabase,
    connect_to_supabase
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "running"}

@app.post("/upload_frame")
async def upload_frame(file: UploadFile = File(...)):
    contents = await file.read()

    np_arr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return {"error": "invalid image"}

    count_value, _ = predict_count(frame) 
    tz = pytz.timezone("Asia/Jakarta")
    now_wib = datetime.now(tz)
    timestamp_wib = int(now_wib.timestamp())

    save_to_supabase(count_value, timestamp_wib)

    return {
        "count": int(count_value),
        "timestamp": timestamp_wib
    }
    
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

@app.get("/summary")
def get_summary():
    conn = connect_to_supabase()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            -- Rata-rata 10 menit terakhir
            COALESCE((
                SELECT AVG(count)
                FROM crowd_logs
                WHERE timestamp >= EXTRACT(EPOCH FROM NOW()) - 600
            ), 0),

            -- peak today
            COALESCE((
                SELECT MAX(count)
                FROM crowd_logs
                WHERE timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))
            ), 0),

            -- avg today
            COALESCE((
                SELECT AVG(count)
                FROM crowd_logs
                WHERE timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))
            ), 0),

            -- lowest today
            COALESCE((
                SELECT MIN(count)
                FROM crowd_logs
                WHERE timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))
            ), 0),
            
            -- 5. Avg Yesterday (rata-rata kemarin penuh)
            COALESCE((
                SELECT AVG(count)
                FROM crowd_logs
                WHERE 
                    timestamp >= EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW() - INTERVAL '1 day'))
                    AND 
                    timestamp < EXTRACT(EPOCH FROM DATE_TRUNC('day', NOW()))
            ), 0)
    """)

    row = cur.fetchone()
    cur.close()
    conn.close()

    return {
        "five_sec": float(row[0]),
        "peak_today": float(row[1]),
        "avg_per_hour": float(row[2]),
        "lowest_today": float(row[3]),
        "avg_yesterday": float(row[4])
    }

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
