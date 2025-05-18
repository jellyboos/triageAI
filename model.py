import os
from dotenv import load_dotenv
from google import genai
from io import BytesIO
from PIL import Image
import base64

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

def generate_triage(bloodPressure, symptoms, images=None):
    try:
        parts = [{
            "text": f"Categorize the patient into a triage level using the Emergency Severity Index (ESI) using the blood pressure: {bloodPressure}, symptoms: {symptoms}, and the images provided. Just display the ESI number and a short explanation for the category in the format: [Integer] - [Explanation based on input]."
        }]

        if images and isinstance(images, list):
            for img_data in images:
                try:
                    # Handle base64 encoded images from frontend
                    if isinstance(img_data, dict) and 'data' in img_data:
                        # Extract base64 data after the comma
                        base64_data = img_data['data'].split(',')[1]
                        img_bytes = base64.b64decode(base64_data)
                        img = Image.open(BytesIO(img_bytes))
                        parts.append(img)
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue

        response = client.models.generate_content(model='gemini-2.0-flash', contents=parts)
        return response.text
    except Exception as e:
        print(f"Error in generate_triage: {str(e)}")
        return "3 - Default triage level due to processing error"