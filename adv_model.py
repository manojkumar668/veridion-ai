import joblib
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.join(BASE_DIR, "ml-model", "model", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "ml-model", "model", "vectorizer.pkl")

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def predict_text(text):
    if not text:
        return {
            "label": "INVALID",
            "confidence": 0,
            "reply": "Empty input received"
        }

    vec = vectorizer.transform([text])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0]

    confidence = round(max(prob) * 100, 2)

    if int(pred) == 1:
        return {
            "label": "FAKE / SCAM",
            "confidence": confidence,
            "reply": "🚨 Suspicious content detected. Avoid sharing personal info."
        }
    else:
        return {
            "label": "REAL NEWS",
            "confidence": confidence,
            "reply": "✅ This appears safe."
        }