import os
import time
import base64
import io
from flask import Flask, render_template, request, jsonify, send_file
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
from PIL import Image

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN")
# Rate limiting: simple in-memory dictionary to store last request time per IP
# In a production app, use Redis or a proper rate limiting library
last_request_time = {}
RATE_LIMIT_SECONDS = 2  # Cooldown between generation requests

def check_rate_limit(ip_address):
    current_time = time.time()
    if ip_address in last_request_time:
        elapsed = current_time - last_request_time[ip_address]
        if elapsed < RATE_LIMIT_SECONDS:
            return False, RATE_LIMIT_SECONDS - elapsed
    last_request_time[ip_address] = current_time
    return True, 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    if not HF_TOKEN:
        return jsonify({'error': 'Server configuration error: HF_TOKEN not set'}), 500

    ip_address = request.remote_addr
    allowed, wait_time = check_rate_limit(ip_address)
    if not allowed:
        return jsonify({'error': f'Please wait {int(wait_time)} seconds before generating another image.'}), 429

    data = request.json
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    try:
        # Initialize the client without a specific provider to allow auto-routing
        client = InferenceClient(
            api_key=HF_TOKEN,
        )

        # Generate image using the specific model requested
        image = client.text_to_image(
            prompt,
            model="black-forest-labs/FLUX.1-schnell",
        )

        # Convert image to base64 for frontend display
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return jsonify({'image': f'data:image/png;base64,{img_str}'})

    except Exception as e:
        print(f"Error generating image: {e}")
        return jsonify({'error': f"Generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
