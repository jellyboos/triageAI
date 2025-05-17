from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
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

if __name__ == "__main__":  # Fixed the string comparison
    app.run(debug=True)