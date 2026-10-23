# Spam SMS Detection

A machine learning project that classifies SMS messages as **Spam** or **Normal (Ham)** using **TF-IDF** and a **Multinomial Naive Bayes** classifier.

## 📌 Project Overview

Spam messages are unwanted messages that may contain advertisements, fraudulent offers, or misleading information.

This project uses Natural Language Processing (NLP) and machine learning to analyze SMS text and predict whether a message is:

- 🚨 Spam
- ✅ Normal (Ham)

The project also provides an interactive Streamlit web application for testing SMS messages.

## ✨ Features

- SMS spam detection using machine learning
- TF-IDF text feature extraction
- Multinomial Naive Bayes classification
- Prediction confidence score
- Interactive Streamlit interface
- User registration and login
- Sample spam and normal messages from the dataset
- Model performance display
- Simple and user-friendly interface

## 🧠 Machine Learning Approach

The project follows these steps:

1. Load the SMS Spam Collection dataset.
2. Remove missing and duplicate records.
3. Separate messages into Spam and Ham classes.
4. Convert SMS text into numerical features using TF-IDF.
5. Split the dataset into training and testing sets.
6. Train a Multinomial Naive Bayes classifier.
7. Evaluate the trained model.
8. Save the trained model and TF-IDF vectorizer.
9. Use the trained model to classify new SMS messages.

## 📊 Dataset

The project uses the **SMS Spam Collection** dataset.

The dataset contains SMS messages labelled as:

- `ham` — Normal message
- `spam` — Spam message

Dataset location:

```text
dataset/spam.csv

After preprocessing, the dataset used for training contains:

5169 messages
4516 Ham messages
653 Spam messages

The data is divided into training and testing sets using an 80/20 stratified split.

📈 Model Performance

The trained Multinomial Naive Bayes model achieved:

Metric	Score
Accuracy	96.62%
Precision	100.00%
Recall	73.28%
F1 Score	84.58%
Confusion Matrix
[[903,   0],
 [ 35,  96]]
🛠️ Technologies Used
Python
Pandas
NumPy
Scikit-learn
Joblib
Streamlit
SQLite
Argon2
Matplotlib
Seaborn
📁 Project Structure
Task_4 Spam SMS Detection/
│
├── app.py
├── auth.py
├── database.py
├── main.py
├── model_comparison.py
├── train_model.py
├── requirements.txt
├── README.md
│
├── dataset/
│   └── spam.csv
│
└── models/
    ├── spam_model.pkl
    └── tfidf_vectorizer.pkl
🚀 How to Run
1. Clone the repository
git clone <your-repository-url>
2. Open the project folder
cd "Task_4 Spam SMS Detection"
3. Create a virtual environment
python -m venv venv
4. Activate the virtual environment

On Windows:

.\venv\Scripts\Activate.ps1
5. Install the required packages
pip install -r requirements.txt
6. Run the Streamlit application
streamlit run app.py

The application will open in your web browser.

🔐 User Authentication

The application includes a basic user authentication system.

Users can:

Register an account
Log in
Use the SMS analyzer
Log out

User information is stored locally using SQLite.

🔍 Application Workflow
Enter SMS Message
       ↓
TF-IDF Vectorization
       ↓
Multinomial Naive Bayes
       ↓
Spam / Normal Prediction
       ↓
Confidence Score
🔮 Future Improvements

Possible future improvements include:

Testing additional machine learning algorithms
Improving spam recall
Adding more advanced text preprocessing
Adding visualizations for important text features
Deploying the application online
Supporting larger and more diverse SMS datasets
👩‍💻 Project

This project was developed as part of a machine learning internship task.