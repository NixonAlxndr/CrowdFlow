from core.yolo_infer import YOLODetector
from core.mcnn_infer import MCNNEstimator
from core.switcher import ConfidenceSwitcher
from core.mcnn_confidence import MCNNConfidence

class HybridCrowdCounter:
    def __init__(self, mcnn_path, yolo_onnx_path):
        self.mcnn = MCNNEstimator(mcnn_path)
        self.yolo = YOLODetector(yolo_onnx_path)
        self.switcher = ConfidenceSwitcher()
        self.mcnn_conf = MCNNConfidence()

    def predict(self, frame):
        mcnn_count = self.mcnn.infer(frame)

        # update temporal confidence
        self.mcnn_conf.update(mcnn_count)
        mcnn_confidence = self.mcnn_conf.compute()

        yolo_result = self.yolo.infer(frame)

        final_count, method = self.switcher.decide(
            mcnn_count=mcnn_count,
            yolo_count=yolo_result["count"],
            yolo_conf=yolo_result["confidence"],
            mcnn_conf=mcnn_confidence
        )

        return {
            "final_count": int(round(final_count)),
            "mcnn_count": int(round(mcnn_count)),
            "mcnn_confidence": mcnn_confidence,
            "yolo_count": yolo_result["count"],
            "yolo_confidence": round(yolo_result["confidence"], 3),
            "method": method
        }