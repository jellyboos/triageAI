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

if __name__ == "__main__":
    print("Starting Flask server on port 5000...") # Debug log
    app.run(debug=True, port=5000, host='0.0.0.0')
