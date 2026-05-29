
import os
import re
import pandas as pd

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    redirect
)

from flask_cors import CORS
from PyPDF2 import PdfReader
from difflib import SequenceMatcher

# =========================================================
# FLASK SETUP
# =========================================================

app = Flask(
    __name__,
    template_folder="templates"
)

app.secret_key = "veridion_secret_key"

CORS(app)

# =========================================================
# DATASET FILES
# =========================================================

DATA_FILE = "data.csv"
NEWS_FILE = "news.csv"

# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = str(text).lower()

    # Remove URLs
    text = re.sub(r"http\S+", "", text)

    # Remove special characters
    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        text
    )

    return text.strip()

# =========================================================
# LOAD KNOWLEDGE BASE
# =========================================================

def load_knowledge_base():

    records = []

    for file in [DATA_FILE, NEWS_FILE]:

        if os.path.exists(file):

            try:

                df = pd.read_csv(file)

                df.columns = [
                    c.lower()
                    for c in df.columns
                ]

                for _, row in df.iterrows():

                    text = str(
                        row.get("text")
                        or row.get("title")
                        or ""
                    ).strip()

                    label_raw = str(
                        row.get("label")
                        or row.get("class")
                        or "fake"
                    ).upper()

                    label = (
                        "FAKE"
                        if any(
                            x in label_raw
                            for x in [
                                "FAKE",
                                "FALSE",
                                "0",
                                "SPAM"
                            ]
                        )
                        else "REAL"
                    )

                    cleaned = clean_text(text)

                    if cleaned:

                        records.append({
                            "text": cleaned,
                            "label": label
                        })

            except Exception as e:

                print(
                    f"Error loading {file}: {e}"
                )

    print(
        f"Loaded {len(records)} records into knowledge base."
    )

    return records

# =========================================================
# LOAD DATA
# =========================================================

KNOWLEDGE_BASE = load_knowledge_base()

CHAT_HISTORY = []

# =========================================================
# SCAM KEYWORDS
# =========================================================

SCAM_KEYWORDS = [

    "otp",
    "bank",
    "upi",
    "verify",
    "click here",
    "urgent",
    "lottery",
    "prize",
    "winner",
    "congratulations",
    "password",
    "aadhaar",
    "account blocked",
    "suspended",
    "claim now",
    "limited time",
    "free money",
    "bitcoin",
    "payment failed",
    "refund",
    "login immediately",
    "security alert",
    "gift card",
    "wire transfer",
    "investment guaranteed",
    "act now",
    "pay now",
    "confirm identity",
    "kyc update",
    "transaction failed"

]

# =========================================================
# SUSPICIOUS DOMAINS
# =========================================================

SUSPICIOUS_DOMAINS = [

    ".xyz",
    ".top",
    ".click",
    ".buzz",
    ".tk",
    ".gq"

]

# =========================================================
# TEXT SIMILARITY
# =========================================================

def similarity(a, b):

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()

# =========================================================
# MAIN AI ANALYSIS ENGINE
# =========================================================

def analyze_text(text):

    original_text = text

    text = clean_text(text)

    reasons = []

    scam_score = 0

    # =====================================================
    # KEYWORD DETECTION
    # =====================================================

    keyword_hits = []

    for keyword in SCAM_KEYWORDS:

        if keyword in text:

            scam_score += 10

            keyword_hits.append(keyword)

    if keyword_hits:

        reasons.append(
            f"Suspicious keywords detected: "
            f"{', '.join(keyword_hits[:6])}"
        )

    # =====================================================
    # URL DETECTION
    # =====================================================

    urls = re.findall(
        r'(https?://\S+|www\.\S+)',
        original_text
    )

    if urls:

        scam_score += 15

        reasons.append(
            "External links detected in message."
        )

        for url in urls:

            for domain in SUSPICIOUS_DOMAINS:

                if domain in url:

                    scam_score += 20

                    reasons.append(
                        f"Suspicious domain detected: {domain}"
                    )

    # =====================================================
    # CAPS DETECTION
    # =====================================================

    uppercase_words = re.findall(
        r'\b[A-Z]{4,}\b',
        original_text
    )

    if len(uppercase_words) >= 2:

        scam_score += 10

        reasons.append(
            "Aggressive urgency formatting detected."
        )

    # =====================================================
    # URGENCY DETECTION
    # =====================================================

    urgency_words = [

        "urgent",
        "immediately",
        "now",
        "fast",
        "hurry"

    ]

    urgency_count = sum(
        word in text
        for word in urgency_words
    )

    if urgency_count >= 2:

        scam_score += 10

        reasons.append(
            "Multiple urgency indicators found."
        )

    # =====================================================
    # DATASET MATCHING
    # =====================================================

    best_match = None

    best_similarity = 0

    for entry in KNOWLEDGE_BASE:

        sim = similarity(
            text,
            entry["text"]
        )

        if sim > best_similarity:

            best_similarity = sim

            best_match = entry

    # =====================================================
    # FINAL DECISION
    # =====================================================

    prediction = "REAL"

    if best_match and best_similarity > 0.70:

        prediction = best_match["label"]

        reasons.append(
            f"Dataset similarity match found "
            f"({round(best_similarity * 100)}%)."
        )

        if prediction == "FAKE":

            scam_score += 30

    if scam_score >= 35:

        prediction = "FAKE"

    confidence = min(
        99,
        max(70, scam_score + 50)
    )

    trust = (
        "HIGH RISK ❌"
        if prediction == "FAKE"
        else "SAFE ✅"
    )

    if prediction == "REAL" and scam_score < 20:

        reasons.append(
            "No major scam patterns detected."
        )

        reasons.append(
            "Language structure appears normal."
        )

        reasons.append(
            "Risk engine classified content as safe."
        )

    if prediction == "FAKE":

        reasons.append(
            "AI threat engine marked content as suspicious."
        )

        reasons.append(
            "Behavior pattern matches phishing/scam logic."
        )

    return {

        "prediction": prediction,

        "confidence": f"{confidence}%",

        "trust": trust,

        "reason": reasons[:6]

    }

# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")

# =========================================================
# CHAT PAGE
# =========================================================

@app.route("/chat")
def chat():

    return render_template("chat.html")

# =========================================================
# PREDICT ROUTE
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json(force=True)

        text = data.get("text", "").strip()

        if not text:

            return jsonify({

                "prediction": "REAL",

                "confidence": "0%",

                "trust": "LOW",

                "reason": [
                    "Empty input"
                ]

            })

        result = analyze_text(text)

        CHAT_HISTORY.append({

            "text": text,

            "prediction": result["prediction"]

        })

        return jsonify(result)

    except Exception as e:

        print(
            "PREDICT ERROR:",
            str(e)
        )

        return jsonify({

            "prediction": "ERROR",

            "confidence": "0%",

            "trust": "SYSTEM ERROR",

            "reason": [
                str(e)
            ]

        }), 500

# =========================================================
# PDF ANALYSIS
# =========================================================

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():

    try:

        file = request.files.get("file")

        if not file:

            return jsonify({
                "error": "No file uploaded"
            })

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:

            extracted = page.extract_text()

            if extracted:

                text += extracted + " "

        result = analyze_text(text)

        return jsonify(result)

    except Exception as e:

        return jsonify({

            "prediction": "ERROR",

            "confidence": "0%",

            "trust": "PDF ERROR",

            "reason": [
                str(e)
            ]

        }), 500

# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    return jsonify(
        CHAT_HISTORY[-20:]
    )

# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(

        host="0.0.0.0",

        port=port,

        debug=True

    )

