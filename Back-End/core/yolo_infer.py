import cv2
import numpy as np
import onnxruntime as ort

class YOLODetector:
    def __init__(self, onnx_path, input_size=640, conf_thres=0.4):
        self.session = ort.InferenceSession(
            onnx_path,
            providers=["CPUExecutionProvider"]
        )
        self.input_size = input_size
        self.conf_thres = conf_thres
        self.input_name = self.session.get_inputs()[0].name

    def preprocess(self, frame):
        img = cv2.resize(frame, (self.input_size, self.input_size))
        img = img[:, :, ::-1]  # BGR → RGB
        img = img.astype(np.float32) / 255.0
        img = np.transpose(img, (2, 0, 1))
        img = np.expand_dims(img, axis=0)
        return img

    def infer(self, frame):
        input_tensor = self.preprocess(frame)
        outputs = self.session.run(None, {self.input_name: input_tensor})

        detections = outputs[0][0]  # [N, 6] → x1,y1,x2,y2,conf,class
        confidences = detections[:, 4]

        valid = confidences > self.conf_thres
        count = int(np.sum(valid))

        avg_conf = float(np.mean(confidences[valid])) if count > 0 else 0.0

        return {
            "count": count,
            "confidence": avg_conf
        }