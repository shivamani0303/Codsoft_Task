from pathlib import Path
import re
import time
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "dataset"
MODEL_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
MODEL_PATH = MODEL_DIR / "movie_genre_model.joblib"

def read_labeled_file(path):
    """Read rows formatted as ID ::: TITLE ::: GENRE ::: DESCRIPTION."""
    rows = []
    skipped = 0
    with open(path, "r", encoding="utf-8", errors="replace") as file:
        for line in file:
            line = line.rstrip("\r\n")
            if not line.strip():
                continue
            parts = line.split(" ::: ", 3)
            if len(parts) != 4:
                skipped += 1
                continue
            movie_id, title, genre, description = parts
            if not genre.strip() or not description.strip():
                skipped += 1
                continue
            rows.append({
                "id": movie_id.strip(),
                "title": title.strip(),
                "genre": genre.strip().lower(),
                "description": description.strip(),
            })
    if skipped:
        print(f"Skipped {skipped} malformed/empty rows in {path.name}.")
    return pd.DataFrame(rows)

def main():
    MODEL_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    train_path = DATA_DIR / "train_data.txt"
    if not train_path.exists():
        raise FileNotFoundError(
            f"Missing {train_path}. Extract the dataset files into the project's dataset folder."
        )

    print("Loading training dataset...")
    data = read_labeled_file(train_path)
    if data.empty:
        raise ValueError("No usable rows were found in train_data.txt.")

    print(f"Loaded {len(data):,} movies across {data['genre'].nunique()} genres.")
    print("Splitting data into training and validation sets...")
    X_train, X_valid, y_train, y_valid = train_test_split(
        data["description"], data["genre"],
        test_size=0.20, random_state=42, stratify=data["genre"]
    )

    # Word n-grams capture genre-related phrases; character n-grams help with spelling variants.
    features = FeatureUnion([
        ("word_tfidf", TfidfVectorizer(
            lowercase=True, stop_words="english",
            ngram_range=(1, 2), max_features=180000,
            min_df=2, sublinear_tf=True
        )),
        ("char_tfidf", TfidfVectorizer(
            analyzer="char_wb", ngram_range=(3, 5),
            max_features=60000, min_df=2, sublinear_tf=True
        )),
    ])

    model = Pipeline([
        ("features", features),
        ("classifier", LinearSVC(class_weight="balanced", random_state=42)),
    ])

    print("Training TF-IDF + LinearSVC. This can take a few minutes...")
    start = time.time()
    model.fit(X_train, y_train)
    print(f"Training finished in {(time.time() - start) / 60:.1f} minutes.")

    print("Evaluating on validation data...")
    predictions = model.predict(X_valid)
    accuracy = accuracy_score(y_valid, predictions)
    print(f"\nValidation accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)")
    report = classification_report(y_valid, predictions, zero_division=0)
    print(report)

    with open(OUTPUT_DIR / "validation_report.txt", "w", encoding="utf-8") as f:
        f.write(f"Validation accuracy: {accuracy:.4f} ({accuracy * 100:.2f}%)\n\n")
        f.write(report)

    joblib.dump(model, MODEL_PATH, compress=3)
    print(f"\nSaved model to: {MODEL_PATH}")
    print("Next: run `streamlit run app.py` to use the app.")

if __name__ == "__main__":
    main()
