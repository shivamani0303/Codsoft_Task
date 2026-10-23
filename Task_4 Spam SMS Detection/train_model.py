import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "dataset" / "spam.csv"

MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "spam_model.pkl"

VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"


# ============================================================
# CREATE MODELS FOLDER
# ============================================================

MODEL_DIR.mkdir(exist_ok=True)


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 60)
print("LOADING DATASET")
print("=" * 60)

df = pd.read_csv(
    DATASET_PATH,
    encoding="latin-1"
)


# ============================================================
# SELECT REQUIRED COLUMNS
# ============================================================

# v1 = label
# v2 = SMS message

df = df[["v1", "v2"]]

df.columns = ["label", "message"]


# ============================================================
# REMOVE MISSING VALUES
# ============================================================

df = df.dropna(
    subset=["label", "message"]
)


# ============================================================
# REMOVE DUPLICATE MESSAGES
# ============================================================

df = df.drop_duplicates(
    subset=["label", "message"]
).reset_index(drop=True)


# ============================================================
# CONVERT LABELS
# ============================================================

# ham  -> 0
# spam -> 1

df["label"] = df["label"].map(
    {
        "ham": 0,
        "spam": 1
    }
)


# Remove rows with invalid labels
df = df.dropna(
    subset=["label"]
)

df["label"] = df["label"].astype(int)


# ============================================================
# DISPLAY DATASET INFORMATION
# ============================================================

print("\nDataset loaded successfully.")

print(
    f"Total messages: {len(df)}"
)

print(
    f"Normal messages (Ham): {(df['label'] == 0).sum()}"
)

print(
    f"Spam messages: {(df['label'] == 1).sum()}"
)


# ============================================================
# INPUT AND TARGET
# ============================================================

X = df["message"]

y = df["label"]


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining messages:", len(X_train))
print("Testing messages:", len(X_test))


# ============================================================
# TF-IDF VECTORIZATION
# ============================================================

print("\n" + "=" * 60)
print("CREATING TF-IDF FEATURES")
print("=" * 60)

tfidf_vectorizer = TfidfVectorizer(
    lowercase=True,
    stop_words="english",
    ngram_range=(1, 2),
    max_features=10000
)


X_train_tfidf = tfidf_vectorizer.fit_transform(
    X_train
)

X_test_tfidf = tfidf_vectorizer.transform(
    X_test
)


print(
    "TF-IDF training shape:",
    X_train_tfidf.shape
)

print(
    "TF-IDF testing shape:",
    X_test_tfidf.shape
)


# ============================================================
# TRAIN MULTINOMIAL NAIVE BAYES
# ============================================================

print("\n" + "=" * 60)
print("TRAINING MULTINOMIAL NAIVE BAYES")
print("=" * 60)

model = MultinomialNB()

model.fit(
    X_train_tfidf,
    y_train
)


print("Model training completed.")


# ============================================================
# PREDICTIONS
# ============================================================

y_pred = model.predict(
    X_test_tfidf
)


# ============================================================
# MODEL EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)


print("\n" + "=" * 60)
print("MODEL PERFORMANCE")
print("=" * 60)

print(
    f"Accuracy : {accuracy * 100:.2f}%"
)

print(
    f"Precision: {precision * 100:.2f}%"
)

print(
    f"Recall   : {recall * 100:.2f}%"
)

print(
    f"F1 Score : {f1 * 100:.2f}%"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\n" + "=" * 60)
print("CLASSIFICATION REPORT")
print("=" * 60)

print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Ham", "Spam"],
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("=" * 60)
print("CONFUSION MATRIX")
print("=" * 60)

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

joblib.dump(
    model,
    MODEL_PATH
)


# ============================================================
# SAVE TF-IDF VECTORIZER
# ============================================================

joblib.dump(
    tfidf_vectorizer,
    VECTORIZER_PATH
)


# ============================================================
# FINAL MESSAGE
# ============================================================

print("\n" + "=" * 60)
print("TRAINING COMPLETED SUCCESSFULLY")
print("=" * 60)

print(
    f"\nModel saved to:\n{MODEL_PATH}"
)

print(
    f"\nTF-IDF vectorizer saved to:\n{VECTORIZER_PATH}"
)

print("\nYour existing app.py can now use these files.")