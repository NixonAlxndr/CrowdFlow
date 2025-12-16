import cv2
from ultralytics import YOLO

model = YOLO("yolo11s.pt")
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame, conf=0.5, iou=0.5)
    detections = results[0].boxes # boxes = kumpulan bounding box hasil deteksi
    
    count_person = 0
    for box in detections:
        cls_id = int(box.cls[0]) # id class object, 0 = people
        confidence = float(box.conf[0]) # confidence model
        if cls_id == 0:
            count_person += 1

            # keep koordinat bounding box
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # bikin bound box
            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            # kasih label bounding box
            cv2.putText(
                frame, 
                "Person",
                (x1, y1-10),
                cv2.FONT_HERSHEY_COMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

    # total count
    cv2.putText(
        frame,
        f"Total Crowd: {count_person}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        3
    )

    cv2.imshow("YOLO v11 Crowd Counting", frame)

    if cv2.waitKey(1) & 0xFF == ord('c'):
        break
    
cap.release()
cv2.destroyAllWindows()
