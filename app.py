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
        # dateOfVisit = datetime.now().strftime("%Y-%m-%d")
        # dob = post_data.get('dob')
        # phoneNumber = post_data.get('phoneNumber')
        # allergies = post_data.get('allergies')
        # meds = post_data.get('meds')
        
        # # Vitals
        # temp = post_data.get('temp')
        # pulse = post_data.get('pulse')
        # respiration = post_data.get('respiration')
        # bloodPressure = post_data.get('bloodPressure')

        # Symptoms
        # Take Symptoms and generate ESI
        # model_response = generate_triage(temp, pulse, respiration, bloodPressure, symptoms).split(" - ")
        # esi_number = model_response[0]
        # esi_explanation = model_response[1]
        # print(esi_number, esi_explanation)
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

if __name__ == "__main__":
    print("Starting Flask server on port 3000...") # Debug log
    app.run(debug=True, port=3000, host='0.0.0.0')