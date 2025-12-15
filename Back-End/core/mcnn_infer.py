import tensorflow as tf
import numpy as np
import cv2

class MCNNEstimator:
    def __init__(self, model_path):
        self.model = tf.keras.models.load_model(model_path)

    def preprocess(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frame.astype(np.float32) / 255.0
        frame = np.expand_dims(frame, axis=0)
        return frame

    def infer(self, frame):
        input_tensor = self.preprocess(frame)
        density_map = self.model.predict(input_tensor, verbose=0)
        count = float(np.sum(density_map))
        return count
