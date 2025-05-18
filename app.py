from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from model import generate_triage
from datetime import datetime
import os
from bson import ObjectId

app = Flask(__name__)
CORS(app)

# In-memory storage as fallback
in_memory_patients = []

# Try to set up MongoDB, but don't fail if it's not available
try:
    from pymongo import MongoClient
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    # Test the connection
    client.server_info()
    db = client["patientdb"]
    # Ensure collection exists
    if "patients" not in db.list_collection_names():
        db.create_collection("patients")
    patients_collection = db["patients"]
    USE_MONGODB = True
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"MongoDB not available, using in-memory storage: {str(e)}")
    USE_MONGODB = False

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
        
        try:
            # Try to generate triage data
            try:
                blood_pressure = f"{patient_doc['vitals']['bloodPressure']['systolic']}/{patient_doc['vitals']['bloodPressure']['diastolic']}"
                symptoms = patient_doc['symptoms']
                model_response = generate_triage(blood_pressure, symptoms, [])
                esi_data = model_response.split(" - ")
                patient_doc['triage'] = {
                    'esiNumber': esi_data[0],
                    'explanation': esi_data[1]
                }
            except Exception as e:
                print(f"Error generating triage: {str(e)}")
                patient_doc['triage'] = {
                    'esiNumber': '3',
                    'explanation': 'Default triage level - triage generation failed'
                }
            
            # Store the patient data
            if USE_MONGODB:
                result = patients_collection.insert_one(patient_doc)
                patient_id = str(result.inserted_id)
            else:
                patient_id = str(len(in_memory_patients))
                in_memory_patients.append(patient_doc)
            
            return jsonify({
                "status": "success",
                "message": "Patient data received and stored!",
                "id": patient_id
            }), 201
            
        except Exception as e:
            print(f"Error storing patient data: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"Failed to store patient data: {str(e)}"
            }), 500
            
    # GET method
    elif request.method == 'GET':
        try:
            if USE_MONGODB:
                patients = list(patients_collection.find({}, {'_id': 0}))
            else:
                patients = in_memory_patients
            return jsonify(patients)
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Failed to retrieve patients: {str(e)}"
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
        
        if USE_MONGODB:
            # Update in MongoDB
            try:
                result = patients_collection.update_one(
                    {'_id': ObjectId(patient_id)},
                    {'$set': {
                        'symptoms': data.get('symptoms'),
                        'notes': data.get('notes'),
                        'status': data.get('status', 'waiting'),
                        'priority': data.get('priority', 3),
                        'updatedAt': datetime.now()
                    }}
                )
                if result.modified_count == 0:
                    return jsonify({
                        "status": "error",
                        "message": "Patient not found"
                    }), 404
            except Exception as e:
                print(f"Error updating patient in MongoDB: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Database error: {str(e)}"
                }), 500
        else:
            # Update in memory
            if patient_id >= len(in_memory_patients):
                return jsonify({
                    "status": "error",
                    "message": "Patient not found"
                }), 404
            patient = in_memory_patients[patient_id]
            patient.update({
                'symptoms': data.get('symptoms'),
                'notes': data.get('notes'),
                'status': data.get('status', 'waiting'),
                'priority': data.get('priority', 3),
                'updatedAt': datetime.now()
            })
        
        return jsonify({
            "status": "success",
            "message": "Patient updated successfully",
            "patient": {
                "id": patient_id,
                "symptoms": data.get('symptoms'),
                "notes": data.get('notes'),
                "status": data.get('status', 'waiting'),
                "priority": data.get('priority', 3)
            }
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