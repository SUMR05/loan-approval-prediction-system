"""
Data cleaning and preprocessing for the Loan Approval Prediction System.

Reads the raw applicant CSV, fixes formatting/type issues, handles missing
values with sensible strategies per column, removes duplicate applications,
and writes a cleaned CSV ready for feature engineering.

Run directly:
    python src/data_preprocessing.py
"""

import json
import os

import pandas as pd

from config import (
    RAW_DATA_PATH,
    CLEANED_DATA_PATH,
    CATEGORICAL_COLUMNS,
    NUMERICAL_COLUMNS,
    MODELS_DIR,
)

IMPUTE_VALUES_PATH = os.path.join(MODELS_DIR, "impute_values.json")


def load_raw_data(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def clean_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip whitespace and normalize casing for categorical/text fields."""
    df = df.copy()
    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": pd.NA, "": pd.NA})

    # Normalize known category values that may appear with inconsistent casing
    df["Gender"] = df["Gender"].str.title()
    df["Married"] = df["Married"].str.title()
    df["Self_Employed"] = df["Self_Employed"].str.title()
    df["Education"] = df["Education"].str.title()
    df["Property_Area"] = df["Property_Area"].str.title()
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset="Applicant_ID", keep="first").reset_index(drop=True)
    removed = before - len(df)
    if removed:
        print(f"Removed {removed} duplicate applicant record(s)")
    return df


def compute_impute_values(df: pd.DataFrame) -> dict:
    """Computes the mode (categorical) / median (numerical) fill values used
    for imputation, so the exact same values can be reused on new applicant
    data at prediction time (see predict.py)."""
    values = {}
    for col in CATEGORICAL_COLUMNS:
        values[col] = df[col].mode(dropna=True)[0]
    for col in NUMERICAL_COLUMNS:
        values[col] = float(df[col].median())
    return values


def handle_missing_values(df: pd.DataFrame, impute_values: dict) -> pd.DataFrame:
    df = df.copy()

    for col in CATEGORICAL_COLUMNS:
        df[col] = df[col].fillna(impute_values[col])

    for col in NUMERICAL_COLUMNS:
        df[col] = df[col].fillna(impute_values[col])

    # Credit_History is conceptually a flag (0/1) - ensure integer type after imputation
    df["Credit_History"] = df["Credit_History"].round().astype(int)
    df["Loan_Amount_Term"] = df["Loan_Amount_Term"].round().astype(int)
    df["Credit_Score"] = df["Credit_Score"].round().astype(int)

    return df


def enforce_valid_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Clip out-of-range values that occasionally occur in real intake data."""
    df = df.copy()
    df["Credit_Score"] = df["Credit_Score"].clip(300, 850)
    df["ApplicantIncome"] = df["ApplicantIncome"].clip(lower=0)
    df["CoapplicantIncome"] = df["CoapplicantIncome"].clip(lower=0)
    df["LoanAmount"] = df["LoanAmount"].clip(lower=1)
    df["Debt_To_Income_Ratio"] = df["Debt_To_Income_Ratio"].clip(0, 2)
    return df


def clean_data(df: pd.DataFrame, impute_values: dict = None) -> pd.DataFrame:
    df = clean_text_columns(df)
    df = remove_duplicates(df)
    if impute_values is None:
        impute_values = compute_impute_values(df)
    df = handle_missing_values(df, impute_values)
    df = enforce_valid_ranges(df)
    return df


def main():
    df = load_raw_data()
    df = clean_text_columns(df)
    df = remove_duplicates(df)

    impute_values = compute_impute_values(df)
    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(IMPUTE_VALUES_PATH, "w", encoding="utf-8") as f:
        json.dump(impute_values, f, indent=2, default=str)

    cleaned = handle_missing_values(df, impute_values)
    cleaned = enforce_valid_ranges(cleaned)

    assert cleaned.isna().sum().sum() == 0, "Cleaned data still contains missing values"

    cleaned.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"Cleaned data saved -> {CLEANED_DATA_PATH}")
    print(f"Final shape: {cleaned.shape[0]} rows, {cleaned.shape[1]} columns")
    print(f"Imputation values saved -> {IMPUTE_VALUES_PATH}")


if __name__ == "__main__":
    main()
