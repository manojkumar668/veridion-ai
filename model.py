import re

SCAM_WORDS = [
    "win",
    "won",
    "winner",
    "lottery",
    "click",
    "link",
    "free",
    "money",
    "withdraw",
    "bank",
    "otp",
    "telegram",
    "whatsapp",
    "crypto",
    "bitcoin",
    "reward",
    "claim",
    "urgent",
    "gift",
    "offer",
    "selected",
    "investment",
    "profit",
    "loan",
    "guaranteed"
]


def predict_text(text):

    text = text.lower()

    matched = []

    score = 0

    for word in SCAM_WORDS:
        if word in text:
            matched.append(word)
            score += 1

    if score >= 2:
        return {
            "prediction": "FAKE",
            "confidence": f"{90 + min(score, 9)}%",
            "reason": [
                "Scam keywords detected",
                f"Matched words: {', '.join(matched)}",
                "Suspicious promotional message",
                "Possible phishing attempt"
            ],
            "trusted": False
        }

    return {
        "prediction": "REAL",
        "confidence": "88%",
        "reason": [
            "No major scam indicators found",
            "Looks like normal communication",
            "Low risk content"
        ],
        "trusted": True
    }