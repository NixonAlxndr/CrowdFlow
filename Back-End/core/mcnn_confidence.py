import math
import numpy as np
from collections import deque

class MCNNConfidence:
    def __init__(self, window_size=12, alpha=2.0):
        """
        window_size = 12 → 1 menit (5 detik × 12)
        alpha       = sensitivity parameter
        """
        self.history = deque(maxlen=window_size)
        self.alpha = alpha

    def update(self, count):
        self.history.append(count)

    def compute(self):
        if len(self.history) < 3:
            return 0.5  # belum cukup konteks temporal

        values = np.array(self.history)

        mean = np.mean(values)
        std = np.std(values)

        # relative variation (noise level)
        variation = std / max(mean, 1)

        # confidence decay
        confidence = math.exp(-self.alpha * variation)

        return round(float(confidence), 3)
