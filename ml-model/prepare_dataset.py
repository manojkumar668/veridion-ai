import pandas as pd

true = pd.read_csv("True.csv")
fake = pd.read_csv("Fake.csv")

true["label"] = 0   # REAL
fake["label"] = 1   # FAKE

df = pd.concat([true, fake])

# Use title + text (important)
df["text"] = df["title"] + " " + df["text"]

df = df[["text", "label"]]
df.to_csv("dataset.csv", index=False)

print("✅ dataset.csv created successfully") 