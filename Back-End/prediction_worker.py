import cv2
import numpy as np
import tensorflow as tf
import psycopg2
import os
import time
from dotenv import load_dotenv

load_dotenv()

# Load PostgreSQL (Supabase)
USER = os.getenv("USER")
PASSWORD = os.getenv("PASSWORD")
HOST = os.getenv("HOST")
PORT = os.getenv("PORT")
DBNAME = os.getenv("DBNAME")

model = tf.keras.models.load_model("mcnn_finetuned.h5", compile=False)

def connect_to_supabase():
    conn = psycopg2.connect(
            user=USER,
            password=PASSWORD,
            host=HOST,
            port=PORT,
            dbname=DBNAME
        )
    return conn

def preprocess(frame):
    img = cv2.resize(frame, (224, 224))
    img = img[..., ::-1]  # BGR -> RGB
    img = img / 255.0
    return np.expand_dims(img, axis=0)

def save_to_supabase(count_value, timestamp):
    try:
        conn = connect_to_supabase()
        cur = conn.cursor()

        query = """
        INSERT INTO crowd_logs (count, timestamp)
        VALUES (%s, %s);
        """

        cur.execute(query, (count_value, timestamp))
        conn.commit()

        cur.close()
        conn.close()

        print("[SUPABASE] Insert OK:", count_value, timestamp)

    except Exception as e:
        print("[SUPABASE] ERROR:", e)
