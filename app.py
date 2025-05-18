from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes with all origins
CORS(app)

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
    print("Received request to /api/patients") # Debug log
    if request.method == 'POST':
        post_data = request.get_json()
        print("Received POST data:", post_data) # Debug log
        firstName = post_data.get('firstName')
        lastName = post_data.get('lastName')
        age = post_data.get('age')
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
    print("Starting Flask server on port 5000...") # Debug log
    app.run(debug=True, port=5000, host='0.0.0.0')
