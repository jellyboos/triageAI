from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from model import generate_triage
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import json

# Custom JSON encoder to handle ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app = Flask(__name__)
app.json_encoder = MongoJSONEncoder
CORS(app)

# MongoDB connection set up
try:
    client = MongoClient("mongodb://localhost:27017/")
    
    # Create or get the database
    db = client["patientdb"]
    
    # Create or get the collection
    if "patients" not in db.list_collection_names():
        patients_collection = db.create_collection("patients")
        print("Created new patients collection")
    else:
        patients_collection = db["patients"]
    
    # Verify connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB and initialized database")
    
except Exception as e:
    print("MongoDB connection/initialization error:", str(e))
    print("Please ensure MongoDB is running on localhost:27017")
    raise Exception("Failed to initialize MongoDB. Application cannot start without database connection.")

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
        try:
            post_data = request.get_json()
            print("Received data:", post_data)  # Debug print
            
            # Personal Info
            firstName = post_data.get('firstName')
            lastName = post_data.get('lastName')
            age = post_data.get('age')
            dateOfBirth = post_data.get('dateOfBirth')
            phoneNumber = post_data.get('phoneNumber')
            timeEntered = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # ISO format for frontend
            dateOfVisit = datetime.now().strftime("%Y-%m-%d")
            
            # Extract vitals information
            vitals = post_data.get('vitals', {})
            
            # Process blood pressure specially if it's in the structured format
            if vitals.get('bloodPressure') and isinstance(vitals['bloodPressure'], dict):
                bp_systolic = vitals['bloodPressure'].get('systolic')
                bp_diastolic = vitals['bloodPressure'].get('diastolic')
                if bp_systolic and bp_diastolic:
                    bloodPressure = f"{bp_systolic}/{bp_diastolic}"
                else:
                    bloodPressure = "N/A"
            else:
                bloodPressure = "N/A"

            # Process symptoms
            symptoms = post_data.get('symptoms', {})
            symptom_text = ""
            if symptoms:
                # Check if symptoms is a string or object
                if isinstance(symptoms, str):
                    symptom_text = symptoms
                else:
                    selected_symptoms = symptoms.get('selected', [])
                    notes = symptoms.get('notes', '')
                    if isinstance(selected_symptoms, list):
                        symptom_text = ", ".join(selected_symptoms)
                    else:
                        symptom_text = str(selected_symptoms)
                    
                    if notes:
                        symptom_text += f". Additional notes: {notes}"

            # Extract additional fields
            allergies = post_data.get('allergies', [])
            medications = post_data.get('medications', [])
            medicalHistory = post_data.get('medicalHistory', [])
            notes = post_data.get('notes', '')

            try:
                # Generate ESI
                model_response = generate_triage(
                    vitals.get('temperature'), 
                    vitals.get('pulse'), 
                    vitals.get('respirationRate'), 
                    bloodPressure, 
                    symptom_text
                ).split(" - ")
                esi_number = ''.join(c for c in model_response[0] if c.isdigit())
                esi_explanation = model_response[1]
            except Exception as e:
                print("Error in generate_triage:", str(e))
                return jsonify({
                    "status": "error",
                    "message": f"Error generating triage: {str(e)}"
                }), 500

            # Create patient record
            patient_record = {
                "firstName": firstName,
                "lastName": lastName,
                "age": age,
                "dateOfBirth": dateOfBirth,
                "phoneNumber": phoneNumber,
                "timeEntered": timeEntered,
                "dateOfVisit": dateOfVisit,
                "vitals": vitals,
                "bloodPressure": bloodPressure,
                "symptoms": symptoms,
                "symptom_text": symptom_text,  # Keep the text version for searching
                "allergies": allergies,
                "medications": medications,
                "medicalHistory": medicalHistory,
                "notes": notes,
                "status": "waiting",  # Default status
                "priority": int(esi_number),  # Use ESI as initial priority
                "esi": esi_number,
                "esi_explanation": esi_explanation
            }

            try:
                # Add to database
                result = patients_collection.insert_one(patient_record)
                patient_record['_id'] = str(result.inserted_id)  # Convert ObjectId to string
            except Exception as e:
                print("Database error:", str(e))
                return jsonify({
                    "status": "error",
                    "message": "Failed to save patient record"
                }), 500

            return jsonify({
                "status": "success",
                "message": "Patient data received!",
                "patient": patient_record
            })

        except Exception as e:
            print("Error processing request:", str(e))
            return jsonify({
                "status": "error",
                "message": f"Server error: {str(e)}"
            }), 500

    # GET method
    elif request.method == 'GET':
        try:
            # Convert MongoDB cursor to list and handle ObjectId serialization
            patients = list(patients_collection.find())
            for patient in patients:
                patient['_id'] = str(patient['_id'])  # Convert ObjectId to string
            
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

@app.route('/api/patients/<patient_id>', methods=['PUT'])
def update_patient(patient_id):
    try:
        data = request.get_json()
        print(f"Received update for patient {patient_id}:", data)  # Debug log
        
        # Convert string ID to ObjectId for MongoDB
        object_id = ObjectId(patient_id)
        
        # Process special fields if needed
        if 'vitals' in data and 'bloodPressure' in data['vitals'] and isinstance(data['vitals']['bloodPressure'], dict):
            bp = data['vitals']['bloodPressure']
            if 'systolic' in bp and 'diastolic' in bp:
                data['bloodPressure'] = f"{bp['systolic']}/{bp['diastolic']}"
        
        # Process symptoms if needed
        if 'symptoms' in data:
            symptoms = data['symptoms']
            if isinstance(symptoms, dict) and 'selected' in symptoms:
                selected = symptoms['selected']
                notes = symptoms.get('notes', '')
                symptom_text = ", ".join(selected) if isinstance(selected, list) else str(selected)
                if notes:
                    symptom_text += f". Additional notes: {notes}"
                data['symptom_text'] = symptom_text
        
        # Update the patient record
        result = patients_collection.update_one(
            {'_id': object_id},
            {'$set': data}
        )
        
        if result.matched_count == 0:
            return jsonify({
                "status": "error",
                "message": "Patient not found"
            }), 404
            
        # Get the updated patient record
        updated_patient = patients_collection.find_one({'_id': object_id})
        if updated_patient:
            updated_patient['_id'] = str(updated_patient['_id'])  # Convert ObjectId to string
            
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
    print("Starting Flask server on port 3000...")  # Debug log
    app.run(debug=True, port=3000, host='0.0.0.0')