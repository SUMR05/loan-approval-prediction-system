"""
Prediction script: scores new loan applicants with the saved best model.

Accepts a CSV of new applicants with the same raw columns as data/raw/loan_data.csv
(minus Loan_Status), runs them through the same cleaning + feature engineering
pipeline used in training, and produces a full loan decision:

    * Final_Decision        - Approved / Partially Approved / Rejected
    * Approved_Amount_INR   - amount approved, in rupees (may be less than requested)
    * Max_Eligible_Amount_INR - max the applicant could afford, in rupees
    * Decision_Reason       - why they were rejected, or why the amount was reduced

The ML model predicts creditworthiness (approve/reject); loan_decision.py
then sizes the approved amount using an affordability rule and generates a
human-readable reason (see src/loan_decision.py).

Usage:
    python src/predict.py --input data/raw/new_applicants_sample.csv --output outputs/new_predictions.csv
    python src/predict.py            # uses the bundled sample applicants if --input is omitted
"""

import argparse
import json
import os
import sys

import joblib
import pandas as pd

# Windows terminals often default to a cp1252 codepage that can't encode the
# rupee sign (Rs symbol) - force UTF-8 stdout so printing decisions never crashes.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import (
    BASE_DIR,
    MODELS_DIR,
    BEST_MODEL_PATH,
    PREPROCESSOR_PATH,
    OUTPUTS_DIR,
    CATEGORICAL_COLUMNS,
    NUMERICAL_COLUMNS,
)
from data_preprocessing import clean_text_columns, handle_missing_values, enforce_valid_ranges
from feature_engineering import engineer_features
import loan_decision

IMPUTE_VALUES_PATH = os.path.join(MODELS_DIR, "impute_values.json")
SAMPLE_NEW_APPLICANTS_PATH = os.path.join(BASE_DIR, "data", "raw", "new_applicants_sample.csv")


def load_new_applicants(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "Loan_Status" in df.columns:
        df = df.drop(columns=["Loan_Status"])
    return df


def preprocess_new_applicants(df: pd.DataFrame) -> pd.DataFrame:
    with open(IMPUTE_VALUES_PATH, "r", encoding="utf-8") as f:
        impute_values = json.load(f)
    # JSON round-trips numeric medians as float/str; cast numeric ones back
    for col in NUMERICAL_COLUMNS:
        impute_values[col] = float(impute_values[col])

    df = clean_text_columns(df)
    df = handle_missing_values(df, impute_values)
    df = enforce_valid_ranges(df)

    # engineer_features one-hot-encodes Employment_Status; keep the human-readable
    # label around so loan_decision can reference it (e.g. "Unemployed") for reasons.
    employment_status_lookup = df.set_index("Applicant_ID")["Employment_Status"]

    df = engineer_features(df)
    df["Employment_Status"] = df["Applicant_ID"].map(employment_status_lookup)
    return df


def predict(df_features: pd.DataFrame) -> pd.DataFrame:
    model = joblib.load(BEST_MODEL_PATH)
    bundle = joblib.load(PREPROCESSOR_PATH)
    preprocessor, feature_columns = bundle["preprocessor"], bundle["feature_columns"]

    # New applicant batches may not contain every category seen in training
    # (e.g. no "Rural" applicants in a small batch) - reindex so one-hot
    # columns line up exactly with what the model was trained on.
    X = df_features.reindex(columns=feature_columns, fill_value=0)
    X_t = preprocessor.transform(X)

    predictions = model.predict(X_t)

    result = df_features.copy()
    result["Predicted_Loan_Status"] = ["Approved" if p == 1 else "Rejected" for p in predictions]

    # Turn the raw creditworthiness prediction into a business decision:
    # how much the applicant is actually approved for (may be less than
    # requested), or why they were rejected.
    decisions = result.apply(
        lambda row: loan_decision.build_decision(row, row["Predicted_Loan_Status"] == "Approved"), axis=1
    )
    result = pd.concat([result, decisions], axis=1)
    return result


def main():
    parser = argparse.ArgumentParser(description="Predict loan approval for new applicants")
    parser.add_argument("--input", default=SAMPLE_NEW_APPLICANTS_PATH, help="CSV of new applicants")
    parser.add_argument(
        "--output", default=os.path.join(OUTPUTS_DIR, "new_predictions.csv"), help="Where to write predictions"
    )
    args = parser.parse_args()

    raw_new = load_new_applicants(args.input)
    featured = preprocess_new_applicants(raw_new)
    result = predict(featured)

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    result.to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Predictions written -> {args.output}\n")

    for _, row in result.iterrows():
        requested = loan_decision.format_inr(row["LoanAmount"] * loan_decision.THOUSAND)
        approved = loan_decision.format_inr(row["Approved_Amount_INR"])
        print(f"{row['Applicant_ID']}  |  Requested: {requested}  "
              f"|  Decision: {row['Final_Decision']}  "
              f"|  Approved Amount: {approved}")
        print(f"    Reason: {row['Decision_Reason']}\n")


if __name__ == "__main__":
    main()
