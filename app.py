from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from model import generate_triage
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB connection set up
client = MongoClient("mongodb://localhost:27017/")
db = client["patientdb"]
patients_collection = db["patient"]

@app.route('/')
def LandingPage():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.json
    return jsonify({"received": data, "status": "success"})

@app.route('/api/patients', methods=['GET', 'POST'])
def patient_data():
    if request.method == 'POST':
        post_data = request.get_json()
        
        # Personal Info
        firstName = post_data.get('firstName')
        lastName = post_data.get('lastName')
        age = post_data.get('age')
        timeEntered = datetime.now().strftime("%H:%M")
        dateOfVisit = datetime.now().strftime("%Y-%m-%d")
        
        # Vitals
        # temp = post_data.get('temp')
        # pulse = post_data.get('pulse')
        # respiration = post_data.get('respiration')
        bloodPressure = str(post_data.get('bloodPressure')['systolic']) + "/" + str(post_data.get('bloodPressure')['diastolic'])

        # Symptoms
        symptoms = post_data.get('symptoms')

        # Images
        images = post_data.get('images')
        # Take Symptoms and generate ESI
        model_response = generate_triage(bloodPressure, symptoms, images).split(" - ")
        esi_number = model_response[0]
        esi_explanation = model_response[1]
        print("ESI num:", esi_number)
        print("ESI explanation:", esi_explanation)
        # Add user to database
        return jsonify({"status": "success", "message": "Patient data received!"})
    return jsonify({"status": "success", "message": "Patient data received!"})

@app.route('/api/message', methods=['GET', 'POST'])
def handle_message():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message', '')
        return jsonify({"response": f"Server received: {message}"})
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    try:
        data = request.get_json()
        print(f"Received update for patient {patient_id}:", data)  # Debug log
        
        # Here you would typically update the patient in your database
        # For now, we'll just return the updated data
        updated_patient = {
            "id": patient_id,
            "symptoms": data.get('symptoms'),
            "notes": data.get('notes'),
            "status": data.get('status', 'waiting'),
            "priority": data.get('priority', 3)
        }
        
        return jsonify({
            "status": "success",
            "message": "Patient updated successfully",
            "patient": updated_patient
        })
    except Exception as e:
        print(f"Error updating patient: {str(e)}")  # Debug log
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    print("Starting Flask server on port 3000...") # Debug log
    app.run(debug=True, port=3000, host='0.0.0.0')