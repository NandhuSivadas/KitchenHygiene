import requests
from decouple import config
import logging

logger = logging.getLogger(__name__)

def call_ml_predict_api(file_path, is_video=False):
    """
    Sends an image or video frame to the external YOLO API for prediction.
    Validates the response format and handles failures gracefully.
    """
    api_url = config('ML_API_URL', default='')
    
    if not api_url:
        logger.error("ML_API_URL not configured in .env")
        return "Service Unavailable", ["ML Service not configured"]

    try:
        with open(file_path, 'rb') as f:
            files = {'image': f}
            # Timeout 10s
            response = requests.post(api_url, files=files, timeout=10)
            
        if response.status_code == 200:
            data = response.json()
            
            # --- VALIDATION ---
            # If the expected key is missing, return 'Invalid Response'
            if "prediction" not in data:
                logger.error(f"Invalid API Response format: {data}")
                return "Invalid Response", ["The AI service returned an unexpected result format."]
                
            prediction = data.get('prediction')
            violations = data.get('violations', [])
            return prediction, violations
            
        else:
            return "Service Unavailable", [f"Server error: {response.status_code}"]

    except (requests.exceptions.RequestException, Exception):
        logger.error("ML API is offline or unreachable")
        return "Service Unavailable", ["The AI analysis service is currently offline."]
