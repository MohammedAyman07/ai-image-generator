import os
import time
import base64
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
MODEL = "@cf/black-forest-labs/flux-1-schnell"

# In-memory cooldown. Use a shared store such as Redis if scaling across instances.
last_request_time = {}
RATE_LIMIT_SECONDS = 2


def check_rate_limit(ip_address):
    current_time = time.time()
    if ip_address in last_request_time:
        elapsed = current_time - last_request_time[ip_address]
        if elapsed < RATE_LIMIT_SECONDS:
            return False, RATE_LIMIT_SECONDS - elapsed
    last_request_time[ip_address] = current_time
    return True, 0


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


def cloudflare_error_message(status, body):
    try:
        payload = json.loads(body)
        errors = payload.get("errors") or []
        details = " ".join(error.get("message", "") for error in errors).lower()
    except (json.JSONDecodeError, AttributeError):
        details = body.decode("utf-8", errors="replace").lower()

    if status == 401 or status == 403:
        return "Cloudflare rejected the API token. Check that it has Workers AI permissions."
    if status == 429 or "quota" in details or "limit" in details:
        return "The free image-generation limit has been reached. Please try again after the daily limit resets."
    return "The image service is temporarily unavailable. Please try again shortly."


@app.route("/generate", methods=["POST"])
def generate_image():
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({
            "error": "Image generation is not configured. Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to the server environment."
        }), 503

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    if len(prompt) > 2048:
        return jsonify({"error": "Prompt must be 2,048 characters or fewer."}), 400

    ip_address = request.remote_addr or "unknown"
    allowed, wait_time = check_rate_limit(ip_address)
    if not allowed:
        return jsonify({
            "error": f"Please wait {max(1, int(wait_time))} seconds before generating another image."
        }), 429

    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{MODEL}"
    )
    body = json.dumps({"prompt": prompt, "steps": 4}).encode("utf-8")
    api_request = Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urlopen(api_request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
        image_data = (result.get("result") or {}).get("image")
        if not image_data:
            app.logger.error("Cloudflare Workers AI response did not include image data")
            return jsonify({"error": "The image service returned an empty result. Please try again."}), 502
        return jsonify({"image": f"data:image/jpeg;base64,{image_data}"})

    except HTTPError as error:
        message = cloudflare_error_message(error.code, error.read())
        app.logger.warning("Cloudflare Workers AI request failed with HTTP %s", error.code)
        return jsonify({"error": message}), 503 if error.code in (401, 402, 403, 429) else 502
    except (URLError, TimeoutError):
        app.logger.exception("Could not reach Cloudflare Workers AI")
        return jsonify({"error": "Could not reach the image service. Please try again shortly."}), 502
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        app.logger.exception("Could not read Cloudflare Workers AI response")
        return jsonify({"error": "The image service returned an invalid response. Please try again."}), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)
