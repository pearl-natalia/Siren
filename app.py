from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)  # This will handle CORS for all routes

@app.route('/', methods=['POST'])
def run_script():
    try:
        # Execute your Python script
        result = subprocess.run(['python3', 'src/record.py'], capture_output=True, text=True, check=True)
        return jsonify({'output': result.stdout, 'error': result.stderr})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e), 'stderr': e.stderr}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
