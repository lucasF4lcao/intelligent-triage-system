from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "mimic-iv-ed-demo-2.2" / "ed"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

triage = pd.read_csv(DATA_DIR / "triage.csv.gz", compression="gzip")

features = ["temperature", "heartrate", "resprate", "o2sat", "sbp", "dbp", "pain"]

df = triage[features + ["acuity"]].copy()
df = df.dropna(subset=["acuity"])

df["target"] = df["acuity"].apply(lambda x: 1 if x <= 2 else 0)

for col in features:
    df[col] = pd.to_numeric(df[col], errors="coerce")
    df[col] = df[col].fillna(df[col].median())

X = df[features]
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

pred = model.predict(X_test)

print("Accuracy:", accuracy_score(y_test, pred))
print("\nClassification Report:\n")
print(classification_report(y_test, pred))
print("Confusion Matrix:\n", confusion_matrix(y_test, pred))

joblib.dump(model, MODEL_DIR / "triagem_model.pkl")
print("\nModelo salvo em models/triagem_model.pkl")
