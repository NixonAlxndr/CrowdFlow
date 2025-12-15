class ConfidenceSwitcher:
    def __init__(
        self,
        low_crowd_threshold=10,
        yolo_conf_threshold=0.6,
        mcnn_conf_threshold=0.55,
        max_discrepancy_ratio=0.35
    ):
        self.low_crowd_threshold = low_crowd_threshold
        self.yolo_conf_threshold = yolo_conf_threshold
        self.mcnn_conf_threshold = mcnn_conf_threshold
        self.max_discrepancy_ratio = max_discrepancy_ratio

    def decide(
        self,
        mcnn_count,
        mcnn_conf,
        yolo_count,
        yolo_conf
    ):
        # 🟢 CASE 1: low crowd → YOLO always
        if max(mcnn_count, yolo_count) < self.low_crowd_threshold:
            return yolo_count, "YOLO (low crowd regime)"

        discrepancy = abs(mcnn_count - yolo_count) / max(mcnn_count, 1)

        # 🔴 MCNN unstable → YOLO
        if (
            mcnn_conf < self.mcnn_conf_threshold and
            yolo_conf >= self.yolo_conf_threshold
        ):
            return yolo_count, "YOLO (MCNN unstable)"

        # 🟡 high discrepancy, both confident
        if (
            mcnn_conf >= self.mcnn_conf_threshold and
            yolo_conf >= self.yolo_conf_threshold and
            discrepancy >= self.max_discrepancy_ratio
        ):
            return yolo_count, "YOLO (discrepancy override)"
        
        # 🟢 default
        return mcnn_count, "MCNN (high crowd stable)"
