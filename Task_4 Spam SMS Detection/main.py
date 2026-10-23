
import joblib
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

# Step 1: Load dataset
data = pd.read_csv(
    "dataset/spam.csv",
    encoding="latin-1",
    usecols=["v1", "v2"]
)

data.columns = ["label", "message"]

# Step 2: Remove duplicate messages
data = data.drop_duplicates()

# Step 3: Convert labels into numerical values
data["label"] = data["label"].map({
    "ham": 0,
    "spam": 1
})

# Step 4: Separate input and output
X = data["message"]
y = data["label"]

# Step 5: Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# Step 6: Convert text into numerical features
tfidf = TfidfVectorizer(
    stop_words="english",
    lowercase=True
)

X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Step 7: Train the model
model = MultinomialNB()
model.fit(X_train_tfidf, y_train)
# Save trained model and TF-IDF vectorizer
os.makedirs("models", exist_ok=True)

joblib.dump(model, "models/spam_model.pkl")
joblib.dump(tfidf, "models/tfidf_vectorizer.pkl")

print("\nModel and vectorizer saved successfully!")
# Step 8: Make predictions
y_pred = model.predict(X_test_tfidf)

# Step 9: Evaluate the model
accuracy = accuracy_score(y_test, y_pred)

print("\n========== SPAM SMS DETECTION ==========")
print(f"\nModel Accuracy: {accuracy * 100:.2f}%")

print("\nClassification Report:")
print(classification_report(
    y_test,
    y_pred,
    target_names=["Ham", "Spam"]
))

# Step 10: Confusion matrix
cm = confusion_matrix(y_test, y_pred)

plt.figure(figsize=(6, 4))

sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=["Ham", "Spam"],
    yticklabels=["Ham", "Spam"]
)

plt.xlabel("Predicted Label")
plt.ylabel("Actual Label")
plt.title("Spam SMS Detection - Confusion Matrix")

plt.tight_layout()
plt.show()

# Step 11: Test custom messages
messages = [
    "Congratulations! You have won a free prize. Claim now!",
    "Hey, are we meeting for lunch today?",
    "URGENT! You have won a cash reward. Call now!",
    "Please bring my notebook tomorrow."
]

messages_tfidf = tfidf.transform(messages)
predictions = model.predict(messages_tfidf)

print("\n========== CUSTOM SMS PREDICTIONS ==========")

for message, prediction in zip(messages, predictions):
    result = "SPAM" if prediction == 1 else "HAM"

    print(f"\nMessage: {message}")
    print(f"Prediction: {result}")