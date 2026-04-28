from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import os
import joblib
import random

app = Flask(__name__, template_folder="templates")
app.secret_key = "veridion_secret_key"
CORS(app)

# ================= BASE PATH =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "ml-model", "model", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "ml-model", "model", "vectorizer.pkl")

print("📦 MODEL PATH:", MODEL_PATH)
print("📦 VECTORIZER PATH:", VECTORIZER_PATH)

# ================= LAZY LOAD MODEL =================
model = None
vectorizer = None

# ================= OTP STORAGE =================
otp_store = {}

# ================= HOME (HEALTH CHECK FOR RENDER) =================
@app.route("/", methods=["GET"])
def home():
    return "Flask ML Backend Running 🚀"

# ================= LOGIN PAGE =================
@app.route('/')
def login():
    return render_template("login.html")

# ================= LOGIN =================
@app.route('/login', methods=['POST'])
def do_login():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"status": "failed", "msg": "No data"}), 400

        email = data.get("email")
        password = data.get("password")

        if email and password:
            session["temp_user"] = email

            otp = str(random.randint(100000, 999999))
            otp_store[email] = otp

            print(f"📩 OTP for {email}: {otp}")

            return jsonify({
                "status": "otp_sent",
                "redirect": "/otp"
            })

        return jsonify({"status": "failed", "msg": "Missing credentials"}), 400

    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

# ================= OTP PAGE =================
@app.route('/otp')
def otp_page():
    return render_template("otp.html")

# ================= VERIFY OTP =================
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    otp = data.get("otp")
    email = session.get("temp_user")

    if email in otp_store and otp_store[email] == otp:
        session["user"] = email
        session.pop("temp_user", None)
        otp_store.pop(email, None)

        return jsonify({"status": "success"})

    return jsonify({"status": "failed", "msg": "Invalid OTP"}), 401

# ================= CHAT PAGE =================
@app.route('/chat')
def chat():
    if "user" not in session:
        return redirect(url_for("login"))

    return render_template("index.html")

# ================= PREDICT API =================
@app.route('/predict', methods=['POST'])
def predict():
    global model, vectorizer

    try:
        # load model once
        if model is None or vectorizer is None:
            print("⚡ Loading ML model...")
            model = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            print("✅ Model Loaded")

        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        text = data.get("text", "")

        if not text:
            return jsonify({"error": "Empty text"}), 400

        vec = vectorizer.transform([text])
        pred = model.predict(vec)[0]
        prob = model.predict_proba(vec)[0]
        confidence = round(max(prob) * 100, 2)

        if int(pred) == 1:
            label = "FAKE / SCAM"
            reply = "🚨 Suspicious Message Detected."
        else:
            label = "REAL NEWS"
            reply = "✅ Safe message."

        return jsonify({
            "prediction": label,
            "confidence": confidence,
            "reply": reply
        })

    except Exception as e:
        print("❌ PREDICT ERROR:", e)
        return jsonify({"error": str(e)}), 500

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

# ================= START SERVER (RENDER FIX) =================
if __name__ == "__main__":
    print("🚀 Starting Flask Server...")

    app.run(
        host="0.0.0.0",   # ✅ IMPORTANT FOR DEPLOYMENT
        port=int(os.environ.get("PORT", 5001)),
        debug=False
    )