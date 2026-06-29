import os

from ultralytics import YOLO
import cv2
from pyzbar.pyzbar import decode

MODEL_PATH = "n_model.pt"
model = YOLO(MODEL_PATH)


def process_image(filepath):

    image = cv2.imread(filepath)

    if image is None:
        return "UNKNOWN", [], None

    ##################################################
    # QR
    ##################################################

    box_number = "UNKNOWN"

    qrs = decode(image)

    if qrs:
        box_number = qrs[0].data.decode("utf-8")

    ##################################################
    # YOLO
    ##################################################

    resized_image = cv2.resize(image, (640, 640))
    results = model(resized_image)

    names = model.names
    boxes = results[0].boxes
    masks = results[0].masks

    class_detections = {}
    for i, cls in enumerate(boxes.cls):
        cls_idx = int(cls.item())
        class_detections.setdefault(cls_idx, []).append(i)

    indices_to_keep = []
    for det_indices in class_detections.values():
        best_idx = max(det_indices, key=lambda i: boxes.conf[i].item())
        indices_to_keep.append(best_idx)

    indices_to_keep.sort()

    if indices_to_keep:
        results[0].boxes = boxes[indices_to_keep]
        if masks is not None:
            results[0].masks = masks[indices_to_keep]

    found_items = []
    for idx in indices_to_keep:
        cls_idx = int(boxes.cls[idx].item())
        item_name = names[cls_idx]
        if item_name not in found_items:
            found_items.append(item_name)

    segmented_image = results[0].plot()

    text1 = f"Box : {box_number}"
    text2 = "Items : " + (", ".join(found_items) if found_items else "none")

    cv2.putText(
        segmented_image,
        text1,
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )
    cv2.putText(
        segmented_image,
        text2,
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    output_name = os.path.splitext(os.path.basename(filepath))[0] + "_segmented.jpg"
    output_path = os.path.join(os.path.dirname(filepath), output_name)
    cv2.imwrite(output_path, segmented_image)

    return box_number, found_items, output_name