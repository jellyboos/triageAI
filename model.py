import os
from dotenv import load_dotenv
from google import genai

# Load environment variables
load_dotenv()

# Get API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

client = genai.Client(api_key=api_key)

def generate_triage(vitals, symptoms):
    response = client.models.generate_content(model = 'gemini-2.0-flash', contents = f"Cateogrize the patient into a triage level using the the Emergency Severity Index (ESI) using the following vitals and symptoms: {symptoms}. Just display the ESI number and a short explanation for the category in the format: [ESI Number] - [Explanation]")
    return response.text
