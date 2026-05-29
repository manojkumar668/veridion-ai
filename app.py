
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
# FLASK APP
# =========================================================

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

app.secret_key = "veridion_secret_key"

CORS(app)

# =========================================================
# FILES
# =========================================================

DATA_FILE = "data.csv"
NEWS_FILE = "news.csv"

# =========================================================
# CLEAN TEXT
# =========================================================

def clean_text(text):

    text = str(text).lower()

    # remove urls
    text = re.sub(r"http\S+", "", text)

    # remove special chars
    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        text
    )

    return text.strip()

# =========================================================
# LOAD DATASET
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

                    if any(
                        x in label_raw
                        for x in [
                            "FAKE",
                            "FALSE",
                            "0",
                            "SPAM"
                        ]
                    ):
                        label = "FAKE"
                    else:
                        label = "REAL"

                    cleaned = clean_text(text)

                    if cleaned:

                        records.append({

                            "text": cleaned,
                            "label": label

                        })

            except Exception as e:

                print(f"ERROR loading {file}: {e}")

    print(f"Loaded {len(records)} records")

    return records

# =========================================================
# GLOBALS
# =========================================================

try:

    KNOWLEDGE_BASE = load_knowledge_base()

except Exception as e:

    print("Knowledge Base Load Error:", e)

    KNOWLEDGE_BASE = []

CHAT_HISTORY = []

# =========================================================
# SCAM KEYWORDS
# =========================================================

SCAM_KEYWORDS = [

    "otp",
    "bank",
    "upi",
    "verify",
    "urgent",
    "lottery",
    "winner",
    "password",
    "aadhaar",
    "claim now",
    "bitcoin",
    "refund",
    "security alert",
    "pay now",
    "kyc update",
    "transaction failed",
    "click here",
    "login immediately",
    "free money"

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
# SIMILARITY FUNCTION
# =========================================================

def similarity(a, b):

    return SequenceMatcher(
        None,
        a,
        b
    ).ratio()

# =========================================================
# ANALYZE TEXT
# =========================================================

def analyze_text(text):

    original_text = text

    text = clean_text(text)

    reasons = []

    scam_score = 0

    # =====================================================
    # KEYWORD CHECK
    # =====================================================

    keyword_hits = []

    for keyword in SCAM_KEYWORDS:

        if keyword in text:

            scam_score += 10
            keyword_hits.append(keyword)

    if keyword_hits:

        reasons.append(
            "Suspicious keywords: "
            + ", ".join(keyword_hits[:5])
        )

    # =====================================================
    # URL CHECK
    # =====================================================

    urls = re.findall(
        r'(https?://\S+|www\.\S+)',
        original_text
    )

    if urls:

        scam_score += 15

        reasons.append(
            "External links detected."
        )

        for url in urls:

            for domain in SUSPICIOUS_DOMAINS:

                if domain in url:

                    scam_score += 20

                    reasons.append(
                        f"Suspicious domain found: {domain}"
                    )

    # =====================================================
    # UPPERCASE CHECK
    # =====================================================

    uppercase_words = re.findall(
        r'\b[A-Z]{4,}\b',
        original_text
    )

    if len(uppercase_words) >= 2:

        scam_score += 10

        reasons.append(
            "Aggressive uppercase formatting."
        )

    # =====================================================
    # URGENCY CHECK
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
            "Urgency indicators detected."
        )

    # =====================================================
    # DATASET MATCH
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

    prediction = "REAL"

    if best_match and best_similarity > 0.70:

        prediction = best_match["label"]

        reasons.append(
            f"Dataset similarity match: "
            f"{round(best_similarity * 100)}%"
        )

        if prediction == "FAKE":

            scam_score += 30

    # =====================================================
    # FINAL PREDICTION
    # =====================================================

    if scam_score >= 35:

        prediction = "FAKE"

    confidence = min(
        99,
        max(60, scam_score + 50)
    )

    trust = (

        "HIGH RISK ❌"

        if prediction == "FAKE"

        else "SAFE ✅"

    )

    if prediction == "FAKE":

        reasons.append(
            "AI engine classified content as scam/phishing."
        )

    else:

        reasons.append(
            "No major scam patterns detected."
        )

    return {

        "prediction": prediction,

        "confidence": f"{confidence}%",

        "trust": trust,

        "reason": reasons[:5]

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
# PREDICT API
# =========================================================

@app.route("/predict", methods=["POST"])
def predict():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "prediction": "ERROR",
                "confidence": "0%",
                "trust": "INVALID REQUEST",
                "reason": ["No JSON received"]

            }), 400

        text = data.get("text", "").strip()

        if not text:

            return jsonify({

                "prediction": "REAL",
                "confidence": "0%",
                "trust": "LOW",
                "reason": ["Empty input"]

            })

        result = analyze_text(text)

        CHAT_HISTORY.append({

            "text": text,
            "prediction": result["prediction"]

        })

        return jsonify(result)

    except Exception as e:

        print("PREDICT ERROR:", str(e))

        return jsonify({

            "prediction": "ERROR",
            "confidence": "0%",
            "trust": "SERVER ERROR",
            "reason": [str(e)]

        }), 500

# =========================================================
# PDF UPLOAD
# =========================================================

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():

    try:

        file = request.files.get("file")

        if not file:

            return jsonify({
                "error": "No file uploaded"
            }), 400

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

            "reason": [str(e)]

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
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({

        "status": "running"

    })

# =========================================================
# RUN APP
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)

