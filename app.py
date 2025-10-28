import os
import requests
from flask import Flask, jsonify, request, send_from_directory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the API key from environment
API_KEY = os.getenv("GEMINI_API_KEY")

# Define the two Google API endpoints
GENERATE_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"
TTS_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={API_KEY}"

# Route 1: Serve the main HTML file
@app.route('/')
def index():
    """Serves the main index.html file."""
    # We rename the HTML file to 'index.html' for simplicity
    return send_from_directory('.', 'index.html')

# Route 2: Proxy for the Text Generation API
@app.route('/api/generate', methods=['POST'])
def api_generate():
    """
    Securely forwards the text generation request to the Gemini API.
    The frontend sends its payload, and this route adds the API key.
    """
    if not API_KEY:
        return jsonify({"error": "Gemini API key not configured on server"}), 500
        
    try:
        # Get the JSON payload from the frontend
        payload = request.get_json()
        
        # Make the request to Google's server
        response = requests.post(GENERATE_URL, json=payload, headers={'Content-Type': 'application/json'})
        
        # Check for a bad response from Google
        response.raise_for_status() 
        
        # Send Google's response back to the frontend
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        # Handle network or HTTP errors
        print(f"Error calling Google API: {e}")
        # Try to return Google's error message if available
        try:
            return jsonify(e.response.json()), e.response.status_code
        except:
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred in /api/generate: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

# Route 3: Proxy for the Text-to-Speech (TTS) API
@app.route('/api/tts', methods=['POST'])
def api_tts():
    """
    Securely forwards the TTS request to the Gemini API.
    """
    if not API_KEY:
        return jsonify({"error": "Gemini API key not configured on server"}), 500
        
    try:
        # Get the JSON payload from the frontend
        payload = request.get_json()
        
        # Make the request to Google's server
        response = requests.post(TTS_URL, json=payload, headers={'Content-Type': 'application/json'})
        
        # Check for a bad response from Google
        response.raise_for_status()
        
        # Send Google's response back to the frontend
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        # Handle network or HTTP errors
        print(f"Error calling Google TTS API: {e}")
        try:
            return jsonify(e.response.json()), e.response.status_code
        except:
            return jsonify({"error": str(e)}), 500
    except Exception as e:
        print(f"An unexpected error occurred in /api/tts: {e}")
        return jsonify({"error": "An internal server error occurred"}), 500

# --- Gunicorn/Localhost Runner ---
if __name__ == '__main__':
    # Get port from environment variables for Render, default to 5000 for local
    port = int(os.environ.get('PORT', 5000))
    # Run on 0.0.0.0 to be accessible on the network (required by Render)
    app.run(debug=True, host='0.0.0.0', port=port)

