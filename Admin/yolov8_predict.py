from ultralytics import YOLO
import os

# === Path setup ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'yolo_models', 'best.pt')

# === Load YOLOv8 model ===
model = YOLO(MODEL_PATH)

# === Hygiene violation labels ===
VIOLATIONS = [
    "rat",
    "cockroach",
    "lizard",
    "no_apron",
    "no_gloves",
    "no_hairnet"
]

def check_hygiene(image_path):
    # Run prediction
    results = model.predict(image_path, save=False, conf=0.25)

    detected_labels = []
    
    # Extract labels from results
    for result in results:
        if result.boxes is not None:
            for box in result.boxes.data:
                cls_id = int(box[5])  # class index
                label = model.names[cls_id]
                detected_labels.append(label)

    # Remove duplicates
    detected_labels = list(set(detected_labels))

    # Filter violations
    violations_found = [label for label in detected_labels if label in VIOLATIONS]
    num_violations = len(violations_found)

    # === Hygiene Rating Logic ===
    if "rat" in violations_found or "cockroach" in violations_found or "lizard" in violations_found:
        status = "Dirty"  # Auto flag critical pests
    elif num_violations >= 3:
        status = "Dirty"
    elif num_violations > 0:
        status = "Moderately Clean"
    else:
        status = "Clean"

    # Debug logs
    print("🔍 Detected Labels:", detected_labels)
    print("🚨 Violations Found:", violations_found)
    print("✅ Hygiene Status:", status)

    return status, detected_labels, violations_found

import cv2
import math

def check_video_hygiene(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return "Error", [], ["Could not open video file"]

    frame_rate = cap.get(cv2.CAP_PROP_FPS) or 30
    target_fps = 1  # Process roughly 1 frame per second
    frame_interval = math.ceil(frame_rate / target_fps)
    
    dirty_frames = 0
    total_processed_frames = 0
    all_violations = set()
    
    count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        if count % frame_interval == 0:
            # Predict on the frame
            results = model.predict(frame, save=False, conf=0.25, verbose=False)
            
            frame_has_violation = False
            for result in results:
                if result.boxes is not None:
                    for box in result.boxes.data:
                        cls_id = int(box[5])
                        label = model.names[cls_id]
                        if label in VIOLATIONS:
                            all_violations.add(label)
                            frame_has_violation = True
            
            if frame_has_violation:
                dirty_frames += 1
            
            total_processed_frames += 1
            
        count += 1
        
    cap.release()
    
    # Decision Logic
    # 1. Critical pests = Dirty immediately
    if "rat" in all_violations or "cockroach" in all_violations or "lizard" in all_violations:
        status = "Dirty"
    # 2. > 30% of frames have violations = Dirty
    elif total_processed_frames > 0 and (dirty_frames / total_processed_frames) > 0.3:
        status = "Dirty"
    # 3. Any violation found = Moderately Clean
    elif len(all_violations) > 0:
        status = "Moderately Clean"
    else:
        status = "Clean"
    
    print(f"🎥 Video Analysis: {dirty_frames}/{total_processed_frames} dirty frames. Status: {status}")
    return status, list(all_violations), list(all_violations)
