# Flask application for patient triage system
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from model import generate_triage, generate_treatment_plan
from pymongo import MongoClient
from datetime import datetime, timedelta
from busyness_predictor import BusynessPredictor
import requests
import pytz
from bson import ObjectId
import json
from map import find_nearest_emergency_rooms

# Custom JSON encoder to handle ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Initialize Flask app with CORS support
app = Flask(__name__)
app.json_encoder = MongoJSONEncoder
CORS(app)

# Reference options for multi-select fields
reference_options = {
    "allergies": [
        "Penicillin", "Latex", "Peanuts", "Shellfish", "Dairy", 
        "Eggs", "Soy", "Tree Nuts", "Wheat/Gluten"
    ],
    "substance_use": ["Alcohol", "Tobacco", "Recreational Drugs"],
    "family_history": [
        "Heart Disease", "Diabetes", "Cancer", "High Blood Pressure", 
        "Stroke", "Mental Health Conditions", "Asthma", "Arthritis"
    ],
    "symptoms": [
        "Fever", "Cough", "Shortness of breath", "Fatigue", "Headache", 
        "Muscle aches", "Sore throat", "Loss of taste/smell", "Nausea", "Diarrhea"
    ]
}

# Reference options for multi-select fields
reference_options = {
    "allergies": [
        "Penicillin", "Latex", "Peanuts", "Shellfish", "Dairy", 
        "Eggs", "Soy", "Tree Nuts", "Wheat/Gluten"
    ],
    "substance_use": ["Alcohol", "Tobacco", "Recreational Drugs"],
    "family_history": [
        "Heart Disease", "Diabetes", "Cancer", "High Blood Pressure", 
        "Stroke", "Mental Health Conditions", "Asthma", "Arthritis"
    ],
    "symptoms": [
        "Fever", "Cough", "Shortness of breath", "Fatigue", "Headache", 
        "Muscle aches", "Sore throat", "Loss of taste/smell", "Nausea", "Diarrhea"
    ]
}

# MongoDB connection setup 
try:
    # Connect to local MongoDB instance
    client = MongoClient("mongodb://localhost:27017/")
    
    # Create or get the database
    db = client["patientdb"]
    
    # Create or get the collection
    if "patients" not in db.list_collection_names():
        patients_collection = db.create_collection("patients")
        print("Created new patients collection")
    else:
        patients_collection = db["patients"]
    
    # Create or update reference options collection
    if "reference_options" not in db.list_collection_names():
        reference_options_collection = db.create_collection("reference_options")
        print("Created new reference_options collection")
    else:
        reference_options_collection = db["reference_options"]
        
    # Insert reference options if collection is empty
    if reference_options_collection.count_documents({}) == 0:
        for category, options in reference_options.items():
            reference_options_collection.insert_one({
                "category": category,
                "options": options
            })
        print("Inserted reference options into database")
    
    # Verify connection
    client.admin.command('ping')
    print("Successfully connected to MongoDB and initialized database")
    
except Exception as e:
    print("MongoDB connection/initialization error:", str(e))
    print("Please ensure MongoDB is running on localhost:27017")
    raise Exception("Failed to initialize MongoDB. Application cannot start without database connection.")

# Route for landing page
@app.route('/')
def LandingPage():
    return render_template('index.html')

# Basic API endpoints for testing
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/data', methods=['POST'])
def post_data():
    data = request.json
    return jsonify({"received": data, "status": "success"})

# API endpoint to get reference options  
@app.route('/api/options/<category>', methods=['GET'])
def get_options(category):
    """Get predefined options for dropdown/checkbox fields."""
    try:
        # Check if category is valid
        valid_categories = ['allergies', 'substance_use', 'family_history', 'symptoms']
        if category not in valid_categories:
            return jsonify({
                "status": "error", 
                "message": f"Invalid category: {category}"
            }), 400
            
        # Get options from database
        option_data = reference_options_collection.find_one({"category": category})
        
        if option_data:
            options = option_data.get("options", [])
        else:
            # Fallback to hardcoded options if not in database
            options = reference_options.get(category, [])
            
        return jsonify({
            "status": "success",
            "options": options
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Main patient data endpoint - handles both GET and POST requests
@app.route('/api/patients', methods=['GET', 'POST'])
def patient_data():
    if request.method == 'POST':
        try:
            post_data = request.get_json()
            print("Received data:", post_data)  # Debug print
            
            # Extract personal information
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
            
            # Extract multi-select fields
            substance_use = post_data.get('substance_use', [])
            family_history = post_data.get('family_history', [])

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

            try:
                # Generate ESI
                treatment_response = generate_treatment_plan(
                    vitals.get('temperature'), 
                    vitals.get('pulse'), 
                    vitals.get('respirationRate'), 
                    bloodPressure, 
                    symptom_text
                )
                print("TREATMENT RESPONSE: ", treatment_response)
            except Exception as e:
                print("Error in generate_treatment_plan:", str(e))
                return jsonify({
                    "status": "error",
                    "message": f"Error generating treatment plan: {str(e)}"
                }), 500
            # Create patient record for database
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
                "esi_explanation": esi_explanation,
                # Add multi-select fields
                "substance_use": substance_use,
                "family_history": family_history
            }

            # Store patient record in MongoDB
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

    # GET method - retrieve all patients
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

# Message handling endpoint
@app.route('/api/message', methods=['GET', 'POST'])
def handle_message():
    if request.method == 'POST':
        data = request.get_json()
        message = data.get('message', '')
        return jsonify({"response": f"Server received: {message}"})
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/patients/<patient_id>', methods=['PUT'])
# Endpoint to update patient information
@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
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
            
        # Update patient information
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
    
def get_busyness_prediction(date=None):
    """
    Get busyness prediction for a given date or next 7 days
    Args:
        date (str, optional): Date in YYYY-MM-DD format. If None, predicts next 7 days
    Returns:
        dict: Predictions with dates and busyness scores
    """
    try:
        # Initialize predictor and load the saved model
        predictor = BusynessPredictor()
        predictor.load_model('busyness_model.pkl')
        
        if date:
            # Single date prediction
            prediction = predictor.predict(date)
            return {
                "date": date,
                "predicted_busyness": round(prediction)
            }
        else:
            # Next 7 days prediction
            today = datetime.now()
            future_dates = [today + timedelta(days=i) for i in range(7)]
            predictions = []
            
            for date in future_dates:
                date_str = date.strftime('%Y-%m-%d')
                prediction = predictor.predict(date_str)
                predictions.append({
                    "date": date_str,
                    "predicted_busyness": round(prediction)
                })
            
            return predictions
            
    except Exception as e:
        print(f"Error in busyness prediction: {str(e)}")
        return None


@app.route('/api/predict/busyness', methods=['GET'])
def predict_busyness():
    try:
        # Get location data first
        location_response = get_location()
        if location_response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": "Failed to get location data"
            }), 500
            
        location_data = location_response.get_json()['location']
        timezone = location_data['timezone']
        
        # Get date parameter from query string (optional)
        date = request.args.get('date')
        if not date:
            # Use timezone-aware current date if no date provided
            tz = pytz.timezone(timezone)
            date = datetime.now(tz).strftime('%Y-%m-%d')
        
        # Get predictions
        predictions = get_busyness_prediction(date)
        
        if predictions is None:
            return jsonify({
                "status": "error",
                "message": "Failed to generate predictions"
            }), 500
            
        # Ensure predictions is always a list
        if not isinstance(predictions, list):
            predictions = [predictions]
            
        return jsonify({
            "status": "success",
            "predictions": predictions,
            "timezone": timezone
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/api/location', methods=['GET'])
def get_location():
    try:
        # Get IP address from request
        ip = request.remote_addr
        
        # Use ipinfo.io instead (more reliable free tier)
        response = requests.get(f'https://ipinfo.io/{ip}/json', 
                              headers={'Accept': 'application/json'})
        print("Location API Response:", response.text)  # Debug print
        data = response.json()
        
        # Extract location and timezone data safely
        loc = data.get('loc', '0,0')
        if loc and ',' in loc:
            lat, lon = loc.split(',')
        else:
            lat, lon = '0', '0'
            
        timezone = data.get('timezone', 'UTC')
        print(timezone)
        
        return jsonify({
            "status": "success",
            "location": {
                "latitude": lat,
                "longitude": lon,
                "timezone": timezone,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "ip": ip
            }
        })
    except Exception as e:
        print(f"Location error: {str(e)}")
        # Fallback to UTC if location service fails
        return jsonify({
            "status": "success",
            "location": {
                "timezone": "UTC",
                "date": datetime.now().strftime('%Y-%m-%d'),
                "ip": ip
            }
        })

@app.route('/api/emergency-rooms', methods=['GET'])
def get_emergency_rooms():
    closet_emergency_rooms = find_nearest_emergency_rooms()
    return closet_emergency_rooms

@app.route('/api/patients/<string:patient_id>/relocate', methods=['DELETE'])
def relocate_patient(patient_id):
    try:
        object_id = ObjectId(patient_id)
        result = patients_collection.delete_one({'_id': object_id})

        if result.deleted_count == 0:
            return jsonify({
                "status": "error",
                "message": "Patient not found or already relocated"
            }), 404

        return jsonify({
            "status": "success",
            "message": "Patient relocated successfully (removed from database)"
        })

    except Exception as e:
        print(f"Error relocating patient: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Start Flask server
if __name__ == "__main__":
    print("Starting Flask server on port 3000...")  # Debug log
    app.run(debug=True, port=3000, host='0.0.0.0')
