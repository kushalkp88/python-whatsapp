import os
import uuid
import base64
import re
import subprocess
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)

# Flask-Limiter setup
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000 per day"]  # Global default: 1000 per day per IP
)
limiter.init_app(app)

def strip_ansi_codes(text):
    """Remove ANSI color codes from a string (for clean QR code output)."""
    ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)

@app.route('/')
def health():
    return "WhatsApp API running!"

@app.route('/qrcode', methods=['GET'])
@limiter.limit("5 per minute")  # Custom limit for QR code endpoint
def qrcode():
    try:
        result = subprocess.run(
            ['node', 'node_whatsapp/send_message.cjs', 'qrcode'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            clean_qr = strip_ansi_codes(result.stdout.strip())
            return jsonify({"qr": clean_qr})
        else:
            return jsonify({"error": result.stderr.strip()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send', methods=['POST'])
@limiter.limit("1000 per day")  # Custom limit for send endpoint
def send():
    data = request.get_json(silent=True) or {}
    phone = request.form.get('phone') or data.get('phone')
    message = request.form.get('message') or data.get('message')
    image_file = request.files.get('image')
    image_base64 = request.form.get('image') or data.get('image')
    scheduled_time = request.form.get('time') or data.get('time')

    if not phone:
        return jsonify({"error": "Phone number is required"}), 400

    if not message and not image_file and not image_base64:
        message = "HI"

    image_path = None
    try:
        if image_file:
            filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            image_file.save(image_path)
        elif image_base64:
            filename = f"{uuid.uuid4()}.png"
            image_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))

        if scheduled_time:
            # TODO: Add scheduling logic here
            return jsonify({"status": "scheduled", "time": scheduled_time})

        cmd = [
            'node', 'node_whatsapp/send_message.cjs', 'send', phone, message or 'HI'
        ]
        if image_path:
            cmd.append(image_path)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if image_path and os.path.exists(image_path):
            os.remove(image_path)

        if result.returncode == 0:
            return jsonify({"status": "sent"})
        else:
            return jsonify({"error": result.stderr.strip() or result.stdout.strip()}), 500

    except Exception as e:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        return jsonify({"error": str(e)}), 500


@app.route('/changesession', methods=['POST'])
@limiter.limit("2 per minute")  # Custom limit for session reset
def changesession():
    try:
        result = subprocess.run(
            ['node', 'node_whatsapp/send_message.cjs', 'changesession'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            return jsonify({"status": "session reset"})
        else:
            return jsonify({"error": result.stderr.strip()}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
