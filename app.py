import os
from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import base64

app = Flask(__name__)
FASTAPI_URL = "https://chris2002-ml-app.hf.space/predict" 
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
        
        # Make API request to your FastAPI endpoint
        api_url = f"{FASTAPI_URL}/predict"
        files = {'file': ('image.jpg', file_content, 'image/jpeg')}
        
        response = requests.post(api_url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("API Response:", result)  # Log the entire response
            
            predicted_class = result.get('predicted_class', 'Unknown')
            confidence = result.get('confidence', 'N/A')
            
            return jsonify({
                "predicted_class": predicted_class,
                "confidence": confidence
            }), 200
        else:
            print(f"API request failed with status code: {response.status_code}")
            print("Response content:", response.text)
            return jsonify({"error": "API request failed"}), response.status_code
    
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to FastAPI: {str(e)}")
        return jsonify({"error": "Failed to connect to classification service"}), 503
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)
