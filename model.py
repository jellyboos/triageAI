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

def generate_triage(temperature, pulse, respiration, bloodPressure, symptoms):
    try:
        parts = [{
            "text": f"Categorize the patient into a triage level using the Emergency Severity Index (ESI) [Level 1 (resuscitation) requires immediate, life-saving intervention and includes patients with cardiopulmonary arrest, major trauma, severe  respiratory distress, and seizures.  Level 2 (emergent) requires an immediate nursing assessment and rapid treatment and includes patients who are in a high-risk situation, are  confused, lethargic, or disoriented, or have severe pain or distress, including  patients with stroke, head injuries, asthma, and sexual-assault injuries.  Level 3 (urgent) includes patients who need quick attention but can wait as long as 30 minutes for assessment and treatment and includes patients with signs of infection, mild respiratory distress, or moderate pain.  Levels 4 and 5 are considered “less urgent” and “non urgent,” respectively. Use the patient's temperature: {temperature}, pulse: {pulse}, respiration: {respiration}, blood pressure: {bloodPressure}, symptoms: {symptoms} to determine the triage level. Just display the ESI number and a short explanation for the category in the format: [Integer] - [Explanation based on input]."
        }]


        response = client.models.generate_content(model='gemini-2.0-flash', contents=parts)
        return response.text
    except Exception as e:
        print(f"Error in generate_triage: {str(e)}")
        return "3 - Default triage level due to processing error"

def find_speicalist(symptoms):
    try:
        parts = [{
            "text": f"if these symptoms deems it needed to call an oncall speicalist, please state the names of the speicalists
            Sample response: oncologist, Sample response when there are mutiple speicalists needed: oncologist,neurologist
            "
        }]


        response = client.models.generate_content(model='gemini-2.0-flash', contents=parts)
        return response.text
    except Exception as e:
        print(f"Error in finding speicalists: {str(e)}")
        return "3 - Default triage level due to processing error"