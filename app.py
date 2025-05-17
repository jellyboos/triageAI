from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def LandingPage():
    return render_template('index.html')



if __name__ == "__main__":  # Fixed the string comparison
    app.run(debug=True)