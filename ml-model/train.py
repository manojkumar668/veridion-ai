import os
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# =========================
# BASE PATH FIX
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# MODEL PATHS
# =========================
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# =========================
# DATA PATHS
# =========================
fake_path = os.path.join(BASE_DIR, "Fake.csv")
true_path = os.path.join(BASE_DIR, "True.csv")

print("📦 Fake PATH:", fake_path)
print("📦 True PATH:", true_path)
print("✔ Fake EXISTS:", os.path.exists(fake_path))
print("✔ True EXISTS:", os.path.exists(true_path))

if not os.path.exists(fake_path) or not os.path.exists(true_path):
    raise FileNotFoundError("❌ Fake.csv or True.csv not found!")

# =========================
# LOAD DATASET
# =========================
fake = pd.read_csv(fake_path)
true = pd.read_csv(true_path)

fake["label"] = 1   # FAKE / SCAM
true["label"] = 0   # REAL NEWS

df = pd.concat([fake, true])

# =========================
# CLEAN DATA
# =========================
df = df.dropna()

# ensure text column exists
if "text" in df.columns:
    X = df["text"]
elif "title" in df.columns:
    X = df["title"]
else:
    X = df.iloc[:, 0]

y = df["label"]

# text cleaning (IMPORTANT FIX)
X = X.astype(str)
X = X.str.lower()
X = X.str.replace(r"http\S+", "", regex=True)
X = X.str.replace(r"\d+", "", regex=True)
X = X.str.strip()

# =========================
# BALANCE DATASET (VERY IMPORTANT FIX)
# =========================
df_clean = pd.DataFrame({"text": X, "label": y})

fake_df = df_clean[df_clean["label"] == 1]
real_df = df_clean[df_clean["label"] == 0]

min_size = min(len(fake_df), len(real_df))

fake_df = fake_df.sample(min_size, random_state=42)
real_df = real_df.sample(min_size, random_state=42)

df_clean = pd.concat([fake_df, real_df])
df_clean = df_clean.sample(frac=1, random_state=42).reset_index(drop=True)

X = df_clean["text"]
y = df_clean["label"]

print("\n📊 Final Dataset Balance:")
print(df_clean["label"].value_counts())

# =========================
# TRAIN TEST SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# TF-IDF VECTORIZER (IMPROVED)
# =========================
vectorizer = TfidfVectorizer(
    stop_words="english",
    ngram_range=(1, 2),
    max_df=0.8,
    min_df=2,
    max_features=50000
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# =========================
# MODEL
# =========================
model = LogisticRegression(
    max_iter=300,
    C=2.0,
    solver="liblinear"
)

model.fit(X_train_vec, y_train)

# =========================
# EVALUATION
# =========================
preds = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, preds)

print("\n🚀 Training Complete!")
print("📊 Accuracy:", round(accuracy * 100, 2), "%")

# =========================
# SAVE MODEL
# =========================
os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(model, MODEL_PATH)
joblib.dump(vectorizer, VECTORIZER_PATH)

print("✅ Model + Vectorizer saved successfully!")