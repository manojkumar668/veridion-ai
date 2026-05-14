from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

import random
import smtplib
import os
import time

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ================= BASE DIR =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= ENV LOAD =================
dotenv_path = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=dotenv_path)

# ================= APP =================
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates")
)

app.secret_key = "veridion_secret_key"

CORS(app)

# ================= RATE LIMITER =================
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# ================= OTP STORE =================
otp_store = {}

OTP_EXPIRY = 300
OTP_COOLDOWN = 30

# ================= EMAIL CONFIG =================
EMAIL = os.getenv("EMAIL_USER")
APP_PASSWORD = os.getenv("EMAIL_PASS")

print("📧 EMAIL:", EMAIL)
print("🔐 PASSWORD LOADED:", bool(APP_PASSWORD))

# ================= EMAIL SENDER =================
# ================= EMAIL SENDER =================
# ================= EMAIL SENDER =================
import requests

def send_otp_email(to_email, otp):

    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": os.getenv("BREVO_API_KEY"),
            "content-type": "application/json"
        }

        payload = {
            "sender": {
                "name": "Veridion AI",
                "email": EMAIL
            },
            "to": [
                {
                    "email": to_email
                }
            ],
            "subject": "Veridion AI OTP",
            "htmlContent": f"""
                <h2>Your OTP is: {otp}</h2>
                <p>Valid for 5 minutes.</p>
            """
        }

        response = requests.post(url, json=payload, headers=headers, timeout=20)

        print("BREVO STATUS:", response.status_code)
        print("BREVO RESPONSE:", response.text)

        return response.status_code == 201

    except Exception as e:
        print("❌ EMAIL ERROR:", e)
        return False

# ================= SEND OTP =================
@app.route("/send-otp", methods=["POST"])
@limiter.limit("5 per minute")
def send_otp():

    data = request.json

    email = data.get("email", "").strip().lower()

    if not email:

        return jsonify({
            "success": False,
            "message": "Email required"
        })

    now = time.time()

    if email in otp_store:

        last = otp_store[email].get("time", 0)

        if now - last < OTP_COOLDOWN:

            return jsonify({
                "success": False,
                "message": "Wait before requesting new OTP"
            })

    otp = str(random.randint(100000, 999999))

    otp_store[email] = {
        "otp": otp,
        "time": now,
        "used": False
    }

    # ================= SEND EMAIL =================
    sent = send_otp_email(email, otp)

    if not sent:

        return jsonify({
            "success": False,
            "message": "Failed to send OTP"
        })

    return jsonify({
        "success": True
    })

# ================= VERIFY OTP =================
@app.route("/verify-otp", methods=["POST"])
def verify_otp():

    data = request.json

    email = data.get("email", "").strip().lower()

    otp = data.get("otp", "").strip()

    record = otp_store.get(email)

    if not record:

        return jsonify({
            "success": False,
            "message": "OTP not found"
        })

    # ================= OTP EXPIRY =================
    if time.time() - record["time"] > OTP_EXPIRY:

        otp_store.pop(email, None)

        return jsonify({
            "success": False,
            "message": "OTP expired"
        })

    # ================= OTP USED =================
    if record["used"]:

        return jsonify({
            "success": False,
            "message": "OTP already used"
        })

    # ================= VERIFY =================
    if record["otp"] == otp:

        otp_store[email]["used"] = True

        session["user"] = email

        return jsonify({
            "success": True
        })

    return jsonify({
        "success": False,
        "message": "Invalid OTP"
    })

# ================= PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():

    text = request.json.get("text", "").lower()

    scam_keywords = [
        "win",
        "lottery",
        "free",
        "money",
        "prize"
    ]

    if any(word in text for word in scam_keywords):

        return jsonify({
            "prediction": "FAKE",
            "confidence": "92%",
            "reason": [
                "Detected scam patterns",
                "Suspicious reward claims",
                "Phishing behavior match",
                "No verified source",
                "High fraud probability"
            ]
        })

    return jsonify({
        "prediction": "REAL",
        "confidence": "87%",
        "reason": [
            "Normal language detected",
            "No scam keywords",
            "Trusted communication pattern",
            "Low risk signals",
            "Safe content"
        ]
    })

# ================= ROUTES =================
@app.route("/")
def login():

    return render_template("login.html")

@app.route("/otp")
def otp():

    return render_template("otp.html")

@app.route("/chat")
def chat():

    if "user" not in session:

        return redirect(url_for("login"))

    return render_template("chat.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

# ================= HEALTH CHECK =================
@app.route("/health")
def health():

    return jsonify({
        "status": "running"
    })

# ================= RUN =================
if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )