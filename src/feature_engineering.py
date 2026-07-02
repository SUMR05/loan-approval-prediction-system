"""
Feature engineering for the Loan Approval Prediction System.

Builds derived financial-risk features on top of the cleaned dataset
(total income, EMI, loan-to-income ratio, balance income after EMI, risk
category) and encodes categorical columns, producing a model-ready CSV.

Run directly:
    python src/feature_engineering.py
"""

import numpy as np
import pandas as pd

from config import CLEANED_DATA_PATH, FEATURED_DATA_PATH


def add_financial_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Total_Income"] = df["ApplicantIncome"] + df["CoapplicantIncome"]

    # Loan amount is stored in thousands; guard against divide-by-zero
    df["Income_To_Loan_Ratio"] = (df["Total_Income"] / (df["LoanAmount"] * 1000).replace(0, np.nan)).fillna(0).round(4)

    df["Loan_Amount_Per_Term"] = (df["LoanAmount"] * 1000 / df["Loan_Amount_Term"]).round(2)

    # Simple flat-rate EMI estimate (principal + notional interest) / term in months
    annual_rate = 0.10
    monthly_rate = annual_rate / 12
    n = df["Loan_Amount_Term"]
    principal = df["LoanAmount"] * 1000
    df["EMI"] = (
        principal * monthly_rate * (1 + monthly_rate) ** n / (((1 + monthly_rate) ** n) - 1)
    ).round(2)

    # ApplicantIncome/CoapplicantIncome (and therefore Total_Income) are monthly figures,
    # matching EMI which is also a monthly installment - no further annualization needed.
    df["Balance_Income"] = (df["Total_Income"] - df["EMI"]).round(2)

    return df


def add_risk_category(df: pd.DataFrame) -> pd.DataFrame:
    """Business-rule risk bucket used for reporting/dashboards (not a model input)."""
    df = df.copy()

    def classify(row):
        if row["Credit_History"] == 0 or row["Credit_Score"] < 580:
            return "High Risk"
        if row["Debt_To_Income_Ratio"] > 0.45 or row["Balance_Income"] < 0:
            return "High Risk"
        if row["Credit_Score"] < 670 or row["Debt_To_Income_Ratio"] > 0.30:
            return "Medium Risk"
        return "Low Risk"

    df["Risk_Category"] = df.apply(classify, axis=1)
    return df


def add_income_and_credit_bands(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["Income_Bracket"] = pd.cut(
        df["Total_Income"],
        bins=[-np.inf, 3000, 6000, 10000, 20000, np.inf],
        labels=["<3K", "3K-6K", "6K-10K", "10K-20K", "20K+"],
    )

    df["Credit_Score_Band"] = pd.cut(
        df["Credit_Score"],
        bins=[0, 579, 669, 739, 799, 850],
        labels=["Poor", "Fair", "Good", "Very Good", "Excellent"],
    )

    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """One-hot encode nominal categorical columns for ML models."""
    df = df.copy()

    df["Dependents"] = df["Dependents"].replace({"3+": "3"}).astype(str)

    binary_maps = {
        "Gender": {"Male": 1, "Female": 0},
        "Married": {"Yes": 1, "No": 0},
        "Education": {"Graduate": 1, "Not Graduate": 0},
        "Self_Employed": {"Yes": 1, "No": 0},
    }
    for col, mapping in binary_maps.items():
        df[col] = df[col].map(mapping)

    df = pd.get_dummies(df, columns=["Employment_Status", "Property_Area", "Dependents"], prefix=[
        "Employment", "Area", "Dependents"
    ])

    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_financial_features(df)
    df = add_risk_category(df)
    df = add_income_and_credit_bands(df)
    df = encode_categoricals(df)
    return df


def main():
    df = pd.read_csv(CLEANED_DATA_PATH)
    featured = engineer_features(df)
    featured.to_csv(FEATURED_DATA_PATH, index=False)
    print(f"Feature-engineered data saved -> {FEATURED_DATA_PATH}")
    print(f"Shape: {featured.shape[0]} rows, {featured.shape[1]} columns")
    print(f"Risk category distribution:\n{featured['Risk_Category'].value_counts()}")


if __name__ == "__main__":
    main()
