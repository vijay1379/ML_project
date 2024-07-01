import os
from flask import Flask, request, jsonify, render_template
import requests
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        # Read file into memory
        file_content = file.read()
        
        # Encode file content as base64
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        
        return jsonify({'file_content': file_content_b64}), 200
    
    except Exception as e:
        print(f"Error handling file: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/classify', methods=['POST'])
def classify():
    try:
        file_content_b64 = request.json['file_content']
        file_content = base64.b64decode(file_content_b64)
        
        # Make API request to the specified endpoint
        api_url = "https://chris2002-ml-app.hf.space/predict"
        response = requests.post(api_url, files={'file': ('image.jpg', file_content, 'image/jpeg')})
        
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

if __name__ == '__main__':
    app.run(debug=True)
