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

def generate_triage(symptoms):
    response = client.models.generate_content(model = 'gemini-2.0-flash', contents = f"Cateogrize the following symptoms into a triage level using the the Emergency Severity Index (ESI): {symptoms}. Just display the ESI number.")
    return response.text

print(generate_triage("trouble breathing, chest pain"))