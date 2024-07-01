import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
from flask import Flask, request, jsonify, render_template, send_from_directory
from PIL import Image
import numpy as np
import os
import uuid
import requests
from io import BytesIO

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict')
def predict():
    return render_template('predict.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        return jsonify({'filename': filename}), 200
    
    except Exception as e:
        print(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/classify', methods=['POST'])
def classify():
    try:
        filename = request.json['filename']
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Read the image file
        with open(filepath, 'rb') as file:
            image_data = file.read()
        
        # Make API request to the specified endpoint
        api_url = "https://chris2002-ml-app.hf.space/predict"
        response = requests.post(api_url, files={'file': ('image.jpg', image_data, 'image/jpeg')})
        
        if response.status_code == 200:
            result = response.json()
            predicted_label = result['predicted_class']
            confidence = result['confidence']
            
            return jsonify({
                "predicted_class": predicted_label,
                "confidence": confidence
            }), 200
        else:
            return jsonify({"error": "API request failed"}), response.status_code
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
