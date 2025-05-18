# Flask application for patient triage system
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from model import generate_triage
from pymongo import MongoClient
from datetime import datetime, timedelta
from busyness_predictor import BusynessPredictor
import requests
import pytz

# Initialize Flask app with CORS support
app = Flask(__name__)
CORS(app)

# MongoDB connection setup
try:
    # Connect to local MongoDB instance
    client = MongoClient("mongodb://localhost:27017/")
    
    # Create or get the database
    db = client["patientdb"]
    
    # Create or get the collection
    if "patient" not in db.list_collection_names():
        patients_collection = db.create_collection("patient")
        print("Created new patients collection")
    else:
        patients_collection = db["patient"]
    
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
            timeEntered = datetime.now().strftime("%H:%M")
            dateOfVisit = datetime.now().strftime("%Y-%m-%d")
            
            # Extract and process vital signs
            temperature = post_data.get('vitals').get('temperature')
            pulse = post_data.get('vitals').get('pulse')
            respiration = post_data.get('vitals').get('respirationRate')
            bloodPressure = None
            if post_data.get('vitals').get('bloodPressure'):
                try:
                    bp_systolic = post_data.get('vitals').get('bloodPressure')['systolic']
                    bp_diastolic = post_data.get('vitals').get('bloodPressure')['diastolic']
                    bloodPressure = str(bp_systolic) + "/" + str(bp_diastolic)
                except Exception as e:
                    print("Error processing blood pressure:", str(e))
                    bloodPressure = "N/A"

            # Process symptoms and notes
            symptoms = post_data.get('symptoms')
            symptom_text = ""
            if symptoms:
                selected_symptoms = symptoms.get('selected', [])
                notes = symptoms.get('notes', '')
                symptom_text = ", ".join(selected_symptoms)
                if notes:
                    symptom_text += f". Additional notes: {notes}"

            # Generate ESI (Emergency Severity Index) using ML model
            try:
                print("Temperature:", temperature)
                print("Pulse:", pulse)
                print("Respiration:", respiration)
                print("Blood pressure:", bloodPressure)
                print("Symptoms:", symptom_text)
                model_response = generate_triage(temperature, pulse, respiration, bloodPressure, symptom_text).split(" - ")
                esi_number = ''.join(c for c in model_response[0] if c.isdigit())
                esi_explanation = model_response[1]
                print("ESI num:", esi_number)
                print("ESI explanation:", esi_explanation)
            except Exception as e:
                print("Error in generate_triage:", str(e))
                return jsonify({
                    "status": "error",
                    "message": f"Error generating triage: {str(e)}"
                }), 500

            # Create patient record for database
            patient_record = {
                "firstName": firstName,
                "lastName": lastName,
                "age": age,
                "timeEntered": timeEntered,
                "dateOfVisit": dateOfVisit,
                "bloodPressure": bloodPressure,
                "symptoms": symptom_text,
                "esi": esi_number,
                "esi_explanation": esi_explanation
            }

            # Store patient record in MongoDB
            try:
                patients_collection.insert_one(patient_record)
            except Exception as e:
                print("Database error:", str(e))
                # Continue even if database insert fails
                pass

            return jsonify({
                "status": "success",
                "message": "Patient data received!",
                "esi": esi_number,
                "explanation": esi_explanation
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
            patients = list(patients_collection.find({}, {'_id': 0}))
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

# Endpoint to update patient information
@app.route('/api/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    try:
        data = request.get_json()
        print(f"Received update for patient {patient_id}:", data)  # Debug log
        
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

# Start Flask server
if __name__ == "__main__":
    print("Starting Flask server on port 3000...") # Debug log
    app.run(debug=True, port=3000, host='0.0.0.0', threaded=True, use_reloader=False)