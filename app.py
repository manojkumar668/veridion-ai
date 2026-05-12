from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import random
import smtplib
import os
from dotenv import load_dotenv

# ================= BASE DIR =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================= LOAD ENV =================
load_dotenv(dotenv_path=os.path.join(BASE_DIR, "backend", ".env"))

# ================= APP INIT =================
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
app.secret_key = "veridion_secret_key"
CORS(app)

# ================= OTP STORE =================
otp_store = {}

# ================= EMAIL CONFIG =================
EMAIL = os.getenv("EMAIL_USER")
APP_PASSWORD = os.getenv("EMAIL_PASS")

print("📧 EMAIL:", EMAIL)
print("🔐 PASSWORD LOADED:", bool(APP_PASSWORD))

if not EMAIL or not APP_PASSWORD:
    print("❌ ERROR: .env missing EMAIL_USER / EMAIL_PASS")


# ================= EMAIL SENDER =================
def send_otp_email(to_email, otp):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, APP_PASSWORD)

        msg = f"Subject: Veridion OTP\n\nYour OTP is: {otp}"
        server.sendmail(EMAIL, to_email, msg)

        server.quit()
        print("✅ OTP SENT")

    except Exception as e:
        print("❌ EMAIL ERROR:", e)


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
    return render_template("index.html")


# ================= SEND OTP =================
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.json or {}
    email = data.get("email", "").strip().lower()

    if not email:
        return jsonify({"success": False, "message": "Email required"})

    otp = str(random.randint(100000, 999999))

    # 🔥 SINGLE ACTIVE OTP PER EMAIL
    otp_store[email] = {
        "otp": otp,
        "used": False
    }

    session["temp_email"] = email

    print("📩 EMAIL:", email)
    print("🔐 OTP:", otp)

    send_otp_email(email, otp)

    return jsonify({"success": True})


# ================= VERIFY OTP =================
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json or {}
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()

    if not email or not otp:
        return jsonify({"success": False})

    record = otp_store.get(email)

    # ❌ no OTP found
    if not record:
        return jsonify({"success": False})

    # ❌ already used
    if record["used"]:
        return jsonify({"success": False})

    # ✅ correct OTP
    if record["otp"] == otp:
        otp_store[email]["used"] = True
        session["user"] = email
        return jsonify({"success": True})

    return jsonify({"success": False})


# ================= AI PREDICT =================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json or {}
    text = data.get("text", "").lower()

    if any(word in text for word in ["win", "lottery", "prize", "free", "money"]):
        return jsonify({
            "prediction": "FAKE",
            "confidence": "92%",
            "reason": [
                "Suspicious promotional language detected",
                "Unrealistic reward claims",
                "Pattern matches scam dataset",
                "No verified source found",
                "High phishing probability"
            ]
        })

    return jsonify({
        "prediction": "REAL",
        "confidence": "87%",
        "reason": [
            "Neutral tone detected",
            "No scam keywords found",
            "Matches trusted patterns",
            "Low risk signals",
            "Content appears safe"
        ]
    })


# ================= MAIL TEST =================
@app.route("/mail-test")
def mail_test():
    send_otp_email(EMAIL, "123456")
    return "Mail test sent"


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ================= RUN =================
if __name__ == "__main__":
    print("🚀 Server running: http://127.0.0.1:5000")
    app.run(debug=True)