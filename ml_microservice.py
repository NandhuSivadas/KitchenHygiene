
from flask import Flask, request, jsonify
from ultralytics import YOLO
import os

app = Flask(__name__)

# --- CONFIGURATION ---
MODEL_PATH = 'Admin/yolo_models/best.pt' # Path to your custom model
PORT = 8000

# Load model once at startup for high performance
if os.path.exists(MODEL_PATH):
    model = YOLO(MODEL_PATH)
    print(f"✅ SUCCESS: YOLO Model loaded from {MODEL_PATH}")
else:
    model = YOLO('yolov8n.pt') 
    print(f"⚠️ WARNING: {MODEL_PATH} not found. Using default yolov8n.pt")

@app.route('/predict/', methods=['POST'])
def predict():
    """
    Endpoint for YOLO inference.
    Expects: Multipart/form-data with key 'image'
    Returns: JSON { prediction, confidence }
    """
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided. Use multipart/form-data with key "image"'}), 400
    
    img_file = request.files['image']
    temp_path = f"process_{img_file.filename}"
    img_file.save(temp_path)

    try:
        # Run YOLOv8 inference
        results = model(temp_path)
        
        # Decision Logic (Customize based on your classes)
        # Example: Class 0=Clean, 1=Moderately Clean, 2=Dirty
        top1_idx = results[0].probs.top1 if hasattr(results[0], 'probs') and results[0].probs else None
        
        if top1_idx is not None:
            # For classification models
            prediction = results[0].names[top1_idx]
            confidence = float(results[0].probs.top1conf)
        else:
            # For detection models (Fallback logic)
            detections = len(results[0].boxes)
            if detections == 0:
                prediction = "Clean"
            elif detections < 3:
                prediction = "Moderately Clean"
            else:
                prediction = "Dirty"
            
            confidence = float(results[0].boxes.conf[0]) if detections > 0 else 1.0

        return jsonify({
            "prediction": prediction,
            "confidence": round(confidence, 2)
        })

    except Exception as e:
        print(f"❌ Error during prediction: {e}")
        return jsonify({'error': str(e)}), 500
    
    finally:
        # Cleanup to keep local storage clean
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == '__main__':
    print(f"🚀 YOLO API Service starting on port {PORT}...")
    app.run(host='0.0.0.0', port=PORT)
