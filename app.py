import os
import time
import json
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

CLOUDFLARE_ACCOUNT_ID = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
MODEL = "@cf/black-forest-labs/flux-1-schnell"
IMAGE_SIZES = {
    "1:1": (1024, 1024),
    "16:9": (1280, 720),
    "9:16": (720, 1280),
}

# In-memory cooldown. Use a shared store such as Redis if scaling across instances.
last_request_time = {}
RATE_LIMIT_SECONDS = 2


class CloudflareRequestError(Exception):
    def __init__(self, status, body):
        self.status = status
        self.details = extract_cloudflare_details(body)
        super().__init__(self.details or f"HTTP {status}")


def extract_cloudflare_details(body):
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError, TypeError):
        return body.decode("utf-8", errors="replace").strip()[:500] if isinstance(body, bytes) else str(body)[:500]

    errors = payload.get("errors") or []
    messages = []
    for error in errors:
        if isinstance(error, dict):
            message = error.get("message")
            code = error.get("code")
            if message:
                messages.append(f"{message} (code {code})" if code else message)
        elif error:
            messages.append(str(error))
    return "; ".join(messages)[:500] or str(payload.get("message", ""))[:500]


def cloudflare_error_message(status, details):
    lowered = (details or "").lower()
    if status == 401:
        return "Cloudflare rejected the API token. Check CLOUDFLARE_API_TOKEN and confirm it has Workers AI permission."
    if status == 403:
        return "Cloudflare denied access to this model. Check the account ID and Workers AI access for the token."
    if status == 400 and ("flagged" in lowered or "safety" in lowered):
        return "Cloudflare blocked this prompt with its safety filter. Please reword the prompt and try again."
    if status == 402 or any(term in lowered for term in ("payment required", "no remaining credits", "insufficient credits")):
        return "Cloudflare reports that this account has no image-generation credits available. Check Workers AI usage and billing in Cloudflare."
    if status == 429 or any(term in lowered for term in ("quota", "daily limit", "neurons exhausted", "rate limit")):
        return "Cloudflare's free daily image-generation quota or rate limit has been reached. Try again after it resets."
    if status >= 500:
        return "Cloudflare's image service is temporarily unavailable. Please try again shortly."
    if details:
        return f"Cloudflare rejected the image request (HTTP {status}): {details}"
    return f"Cloudflare rejected the image request (HTTP {status}). Check the Cloudflare Workers AI settings."


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


def make_multipart_body(fields, boundary):
    chunks = []
    for name, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode("utf-8"),
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"),
            str(value).encode("utf-8"),
            b"\r\n",
        ])
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks)


def request_cloudflare_image(model, prompt, width, height):
    boundary = "----AymanImageGeneration" + uuid.uuid4().hex
    body = make_multipart_body({
        "prompt": prompt,
        "width": width,
        "height": height,
    }, boundary)
    endpoint = (
        "https://api.cloudflare.com/client/v4/accounts/"
        f"{CLOUDFLARE_ACCOUNT_ID}/ai/run/{model}"
    )
    api_request = Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urlopen(api_request, timeout=120) as response:
            result = json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise CloudflareRequestError(error.code, error.read()) from None

    image_data = (result.get("result") or {}).get("image")
    if not image_data:
        raise ValueError("Cloudflare returned a successful response without image data.")
    return image_data


@app.route("/generate", methods=["POST"])
def generate_image():
    if not CLOUDFLARE_ACCOUNT_ID or not CLOUDFLARE_API_TOKEN:
        return jsonify({
            "error": "Image generation is not configured. Add CLOUDFLARE_ACCOUNT_ID and CLOUDFLARE_API_TOKEN to the server environment."
        }), 503

    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    ratio = data.get("ratio", "1:1")
    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400
    if len(prompt) > 2048:
        return jsonify({"error": "Prompt must be 2,048 characters or fewer."}), 400
    if ratio not in IMAGE_SIZES:
        return jsonify({"error": "Choose a supported aspect ratio."}), 400

    ip_address = request.remote_addr or "unknown"
    allowed, wait_time = check_rate_limit(ip_address)
    if not allowed:
        return jsonify({
            "error": f"Please wait {max(1, int(wait_time))} seconds before generating another image."
        }), 429

    width, height = IMAGE_SIZES[ratio]
    try:
        image_data = request_cloudflare_image(MODEL, prompt, width, height)
        return jsonify({
            "image": f"data:image/jpeg;base64,{image_data}",
            "model": MODEL,
        })

    except CloudflareRequestError as error:
        app.logger.warning(
            "Workers AI request failed with HTTP %s: %s",
            error.status,
            error.details,
        )
        message = cloudflare_error_message(error.status, error.details)
        if error.status == 429 or "daily" in message.lower():
            status_code = 429
        elif error.status in (401, 402, 403):
            status_code = 503
        else:
            status_code = 502
        return jsonify({"error": message}), status_code
    except (URLError, TimeoutError):
        app.logger.exception("Could not reach Cloudflare Workers AI")
        return jsonify({"error": "Could not reach Cloudflare. Check the Vercel function logs and try again shortly."}), 502
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        app.logger.exception("Could not read Cloudflare Workers AI response")
        return jsonify({"error": "Cloudflare returned an invalid image response. Check the Vercel function logs for details."}), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)
