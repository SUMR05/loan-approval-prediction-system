"""
Trains and compares three classification models for loan approval prediction:
Logistic Regression, Decision Tree, and Random Forest.

Each model is evaluated on Accuracy, Precision, Recall, F1-score and a
confusion matrix. The best model (highest F1-score) is saved with joblib
for use by predict.py, along with the fitted preprocessing pipeline and
run metadata.

Run directly:
    python src/train_models.py
"""

import json
import os

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

from config import (
    FEATURED_DATA_PATH,
    ID_COLUMN,
    TARGET_COLUMN,
    RANDOM_STATE,
    TEST_SIZE,
    MODELS_DIR,
    BEST_MODEL_PATH,
    PREPROCESSOR_PATH,
    MODEL_METADATA_PATH,
    OUTPUTS_DIR,
    EVALUATION_REPORT_PATH,
    MODEL_COMPARISON_CSV,
    CONFUSION_MATRIX_DIR,
)
from model_evaluation import compute_metrics, plot_confusion_matrix, build_text_report

# Columns that are identifiers or human-readable reporting fields, not model inputs
NON_FEATURE_COLUMNS = [ID_COLUMN, TARGET_COLUMN, "Risk_Category", "Income_Bracket", "Credit_Score_Band"]

NUMERIC_FEATURES_TO_SCALE = [
    "ApplicantIncome", "CoapplicantIncome", "LoanAmount", "Loan_Amount_Term",
    "Credit_Score", "Existing_Loans_Count", "Years_At_Current_Job",
    "Debt_To_Income_Ratio", "Total_Income", "Income_To_Loan_Ratio",
    "Loan_Amount_Per_Term", "EMI", "Balance_Income",
]


def load_features():
    df = pd.read_csv(FEATURED_DATA_PATH)
    X = df.drop(columns=NON_FEATURE_COLUMNS)
    y = (df[TARGET_COLUMN] == "Y").astype(int)
    feature_columns = list(X.columns)
    return X, y, feature_columns


def build_preprocessor(feature_columns):
    scale_cols = [c for c in NUMERIC_FEATURES_TO_SCALE if c in feature_columns]
    passthrough_cols = [c for c in feature_columns if c not in scale_cols]
    return ColumnTransformer(
        transformers=[
            ("scale", StandardScaler(), scale_cols),
            ("passthrough", "passthrough", passthrough_cols),
        ]
    )


def get_models():
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, min_samples_leaf=20, random_state=RANDOM_STATE),
        "Random Forest": RandomForestClassifier(
            n_estimators=300, max_depth=10, min_samples_leaf=10, random_state=RANDOM_STATE, n_jobs=-1
        ),
    }


def main():
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    X, y, feature_columns = load_features()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    preprocessor = build_preprocessor(feature_columns)
    preprocessor.fit(X_train)
    joblib.dump({"preprocessor": preprocessor, "feature_columns": feature_columns}, PREPROCESSOR_PATH)

    X_train_t = preprocessor.transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    results = {}
    fitted_models = {}

    for name, model in get_models().items():
        model.fit(X_train_t, y_train)
        y_pred = model.predict(X_test_t)

        metrics = compute_metrics(y_test, y_pred)
        cm_path = plot_confusion_matrix(y_test, y_pred, name, CONFUSION_MATRIX_DIR)

        results[name] = {"metrics": metrics, "y_true": y_test, "y_pred": y_pred, "confusion_matrix_path": cm_path}
        fitted_models[name] = model

        print(f"{name:22s} | Accuracy={metrics['accuracy']:.4f}  Precision={metrics['precision']:.4f}  "
              f"Recall={metrics['recall']:.4f}  F1={metrics['f1_score']:.4f}")

    # Best model selection: highest F1-score (balances precision/recall for loan risk decisions)
    best_model_name = max(results, key=lambda n: results[n]["metrics"]["f1_score"])
    best_model = fitted_models[best_model_name]
    print(f"\nBest model selected: {best_model_name}")

    joblib.dump(best_model, BEST_MODEL_PATH)

    comparison_df = pd.DataFrame(
        {name: r["metrics"] for name, r in results.items()}
    ).T.reset_index().rename(columns={"index": "model"})
    comparison_df.to_csv(MODEL_COMPARISON_CSV, index=False)

    report_text = build_text_report(results, best_model_name)
    with open(EVALUATION_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)

    metadata = {
        "best_model": best_model_name,
        "metrics": results[best_model_name]["metrics"],
        "feature_columns": feature_columns,
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "random_state": RANDOM_STATE,
    }
    with open(MODEL_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\nModel comparison saved -> {MODEL_COMPARISON_CSV}")
    print(f"Evaluation report saved -> {EVALUATION_REPORT_PATH}")
    print(f"Best model saved -> {BEST_MODEL_PATH}")
    print(f"Preprocessor saved -> {PREPROCESSOR_PATH}")


if __name__ == "__main__":
    main()
