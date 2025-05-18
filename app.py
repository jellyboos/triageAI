from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from model import generate_triage
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MongoDB connection set up
try:
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
            timeEntered = datetime.now().strftime("%H:%M")
            dateOfVisit = datetime.now().strftime("%Y-%m-%d")
            
            # Vitals
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

            # Symptoms
            symptoms = post_data.get('symptoms')
            symptom_text = ""
            if symptoms:
                selected_symptoms = symptoms.get('selected', [])
                notes = symptoms.get('notes', '')
                symptom_text = ", ".join(selected_symptoms)
                if notes:
                    symptom_text += f". Additional notes: {notes}"

            # Images
            
            try:
                # Generate ESI
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

            # Create patient record
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

            try:
                # Add to database
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
    print("Starting Flask server on port 3000...") # Debug log
    app.run(debug=True, port=3000, host='0.0.0.0')