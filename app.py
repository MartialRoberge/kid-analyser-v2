from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import subprocess
import json
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the absolute path of the project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Configuration with absolute paths
UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}
JSON_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'LLM', 'outputs', 'kid.json')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def run_pipeline(pdf_path):
    """Run the analysis pipeline on the uploaded PDF."""
    try:
        print(f"Processing PDF: {pdf_path}")

        # Run the pipeline script
        print("Running pipeline script...")
        result = subprocess.run(['./run_pipeline.sh', pdf_path], 
                             capture_output=True, 
                             text=True)
        print(f"Pipeline script output:\n{result.stdout}")
        print(f"Pipeline script error:\n{result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Pipeline failed: {result.stderr}")

        # Read and return the JSON output
        with open(JSON_OUTPUT_PATH, 'r') as f:
            return json.load(f)

    except Exception as e:
        raise Exception(f"Error running pipeline: {str(e)}")

@app.route('/analyze', methods=['POST'])
def analyze_pdf():
    """Endpoint to analyze a PDF file."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Create upload folder if it doesn't exist
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Process the PDF and get results
            result = run_pipeline(file_path)
            return jsonify(result)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            # Clean up uploaded file
            if os.path.exists(file_path):
                os.remove(file_path)
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/kid-json', methods=['GET'])
def get_kid_json():
    """Endpoint to get the latest kid.json file."""
    try:
        return send_file(JSON_OUTPUT_PATH, mimetype='application/json')
    except Exception as e:
        return jsonify({'error': f'Error reading kid.json: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
