# CodSoft Task 1 — Movie Genre Classification

A text-classification project that predicts a movie genre from its plot description.

## Project contents

- `dataset/train_data.txt` — labeled training data
- `dataset/test_data.txt` — unlabeled test descriptions supplied with the dataset
- `dataset/test_data_solution.txt` — labels for the supplied test set
- `train_model.py` — trains and evaluates the TF-IDF + LinearSVC model
- `app.py` — Streamlit interface for interactive genre predictions
- `requirements.txt` — Python dependencies
- `models/` — trained model is saved here after training
- `outputs/` — validation report is saved here after training

## Requirements

- Python 3.10 or newer recommended
- VS Code
- Internet access for the first-time library installation

## Setup in VS Code (Windows PowerShell)

Open this project folder in VS Code. In Terminal → New Terminal, run:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Train the model

```powershell
.\.venv\Scripts\python.exe train_model.py
```

Training may take a few minutes, depending on the computer. It prints validation accuracy and a classification report. The trained model is saved to `models/movie_genre_model.joblib`.

### Start the app

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Streamlit opens the app in your browser. Enter a plot summary and click **Predict genre**.

## Dataset format

The provided files use ` ::: ` separators:

- Training: `ID ::: TITLE ::: GENRE ::: DESCRIPTION`
- Test input: `ID ::: TITLE ::: DESCRIPTION`
- Test solution: `ID ::: TITLE ::: GENRE ::: DESCRIPTION`

The training script uses `split(" ::: ", 3)` so separators within a description are less likely to break parsing.

## Model approach

- Word-level TF-IDF features (unigrams and bigrams)
- Character-level TF-IDF features (character n-grams)
- Linear Support Vector Classifier (LinearSVC)
- Stratified 80/20 train-validation split with a fixed random seed

The validation score is calculated from this dataset split. It is not a promise of accuracy on every real-world movie plot. The test solution file is included for reference, but this starter project does not automatically train on the test set.

## Notes

- The model is **not pre-trained** in this ZIP. Run `train_model.py` once to create it.
- `models/movie_genre_model.joblib` and `outputs/validation_report.txt` are generated when training completes.
- Do not commit the dataset or generated model to GitHub unless your internship instructions and repository size limits permit it.
- Predictions can be imperfect because genres overlap and descriptions may be noisy.
