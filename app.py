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
patients_collection = db["patients"]

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
        
        # Create patient document
        patient_doc = {
            # Personal Information
            'firstName': post_data.get('firstName'),
            'lastName': post_data.get('lastName'),
            'dateOfVisit': datetime.now().strftime("%Y-%m-%d"),
            'dateOfBirth': post_data.get('dateOfBirth'),
            'phoneNumber': post_data.get('phoneNumber'),
            
            # Medical Information/Vitals
            'vitals': {
                'temperature': post_data.get('vitals', {}).get('temperature'),
                'pulse': post_data.get('vitals', {}).get('pulse'),
                'respirationRate': post_data.get('vitals', {}).get('respirationRate'),
                'bloodPressure': post_data.get('vitals', {}).get('bloodPressure')
            },
            
            # Allergies and Medications
            'allergies': {
                'selected': post_data.get('allergies', {}).get('selected', []),
                'other': post_data.get('allergies', {}).get('other')
            },
            'medications': {
                'current': post_data.get('medications', {}).get('current')
            },
            
            # Medical History
            'medicalHistory': {
                'substanceUse': post_data.get('medicalHistory', {}).get('substanceUse', {}),
                'familyHistory': post_data.get('medicalHistory', {}).get('familyHistory', {}),
                'surgeries': post_data.get('medicalHistory', {}).get('surgeries'),
                'complications': post_data.get('medicalHistory', {}).get('complications')
            },
            
            # Symptoms
            'symptoms': post_data.get('symptoms', {}),
            
            # Metadata
            'createdAt': datetime.now(),
            'updatedAt': datetime.now()
        }
        
        # Insert into MongoDB
        try:
            result = patients_collection.insert_one(patient_doc)
            print(f"Patient document inserted with id: {result.inserted_id}")
            
            # Generate triage data if needed
            blood_pressure = f"{patient_doc['vitals']['bloodPressure']['systolic']}/{patient_doc['vitals']['bloodPressure']['diastolic']}"
            symptoms = patient_doc['symptoms']
            model_response = generate_triage(blood_pressure, symptoms, [])
            esi_data = model_response.split(" - ")
            
            # Update document with triage data
            patients_collection.update_one(
                {'_id': result.inserted_id},
                {
                    '$set': {
                        'triage': {
                            'esiNumber': esi_data[0],
                            'explanation': esi_data[1]
                        }
                    }
                }
            )
            
            return jsonify({
                "status": "success",
                "message": "Patient data received and stored!",
                "id": str(result.inserted_id)
            }), 201
            
        except Exception as e:
            print(f"Error storing patient data: {str(e)}")
            return jsonify({
                "status": "error",
                "message": "Failed to store patient data"
            }), 500
            
    # GET method
    elif request.method == 'GET':
        try:
            patients = list(patients_collection.find({}, {'_id': 0}))
            return jsonify(patients)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": "Failed to retrieve patients"
            }), 500

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
    print("Starting Flask server on port 3000...")
    app.run(debug=True, port=3000, host='0.0.0.0')