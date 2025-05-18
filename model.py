import os
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image
import base64

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')

def generate_triage(bloodPressure, symptoms, images=None):
    if not api_key:
        print("Warning: GOOGLE_API_KEY not found. Using default triage level.")
        return "3 - Default triage level (API key not configured)"
        
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        
        parts = [{
            "text": f"Categorize the patient into a triage level using the Emergency Severity Index (ESI) using the blood pressure: {bloodPressure}, symptoms: {symptoms}, and the images provided. Just display the ESI number and a short explanation for the category in the format: [Integer] - [Explanation based on input]."
        }]

        if images:
            for img_file in images:
                if hasattr(img_file, "read"):  # e.g., werkzeug.datastructures.FileStorage
                    pil_img = Image.open(BytesIO(img_file.read()))
                    parts.append(pil_img)
                elif isinstance(img_file, BytesIO):
                    pil_img = Image.open(img_file)
                    parts.append(pil_img)
        response = client.models.generate_content(model = 'gemini-2.0-flash', contents = parts)
        return response.text
    except Exception as e:
        print(f"Error generating triage with Gemini: {str(e)}")
        return "3 - Default triage level (Error generating triage)"
