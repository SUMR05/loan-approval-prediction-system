"""
Builds a single flat, Power-BI-ready CSV from the feature-engineered dataset
plus the trained model's predictions, so the dashboard can show both actual
historical outcomes and model-predicted outcomes side by side.

Run directly (after train_models.py has produced a saved model):
    python src/generate_powerbi_data.py
"""

import sys

import joblib
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from config import (
    FEATURED_DATA_PATH,
    POWERBI_DATA_PATH,
    BEST_MODEL_PATH,
    PREPROCESSOR_PATH,
    ID_COLUMN,
    TARGET_COLUMN,
)
import loan_decision

NON_FEATURE_COLUMNS = [ID_COLUMN, TARGET_COLUMN, "Risk_Category", "Income_Bracket", "Credit_Score_Band"]


def add_model_predictions(df: pd.DataFrame) -> pd.DataFrame:
    model = joblib.load(BEST_MODEL_PATH)
    bundle = joblib.load(PREPROCESSOR_PATH)
    preprocessor, feature_columns = bundle["preprocessor"], bundle["feature_columns"]

    X = df.reindex(columns=feature_columns, fill_value=0)
    X_t = preprocessor.transform(X)

    df = df.copy()
    df["Predicted_Loan_Status"] = ["Approved" if p == 1 else "Rejected" for p in model.predict(X_t)]
    return df


def add_decision_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Restores human-readable Employment_Status/Property_Area labels (lost to
    one-hot encoding during feature engineering), then runs the affordability
    decision (approved amount / rejection reason) from loan_decision.py."""
    df = df.copy()

    employment_cols = [c for c in df.columns if c.startswith("Employment_")]
    df["Employment_Status"] = df[employment_cols].idxmax(axis=1).str.replace("Employment_", "", regex=False)

    area_cols = [c for c in df.columns if c.startswith("Area_")]
    df["Property_Area"] = df[area_cols].idxmax(axis=1).str.replace("Area_", "", regex=False)

    decisions = df.apply(
        lambda row: loan_decision.build_decision(row, row["Predicted_Loan_Status"] == "Approved"), axis=1
    )
    return pd.concat([df, decisions], axis=1)


def build_dashboard_dataset(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Loan_Status_Label"] = df[TARGET_COLUMN].map({"Y": "Approved", "N": "Rejected"})
    df["Gender_Label"] = df["Gender"].map({1: "Male", 0: "Female"})
    df["Married_Label"] = df["Married"].map({1: "Yes", 0: "No"})
    df["Education_Label"] = df["Education"].map({1: "Graduate", 0: "Not Graduate"})

    # LoanAmount is stored in thousands of rupees; convert to full rupees for the dashboard,
    # matching Max_Eligible_Amount_INR / Approved_Amount_INR from loan_decision.py.
    df["LoanAmount_INR"] = (df["LoanAmount"] * loan_decision.THOUSAND).round().astype(int)

    dashboard_cols = [
        ID_COLUMN,
        "Gender_Label", "Married_Label", "Education_Label", "Employment_Status", "Property_Area",
        "ApplicantIncome", "CoapplicantIncome", "Total_Income", "Income_Bracket",
        "LoanAmount_INR", "Loan_Amount_Term", "EMI", "Balance_Income",
        "Credit_Score", "Credit_Score_Band", "Credit_History",
        "Debt_To_Income_Ratio", "Existing_Loans_Count", "Years_At_Current_Job",
        "Risk_Category",
        "Loan_Status_Label", "Predicted_Loan_Status",
        "Max_Eligible_Amount_INR", "Approved_Amount_INR", "Final_Decision", "Decision_Reason",
    ]
    out = df[dashboard_cols].rename(
        columns={
            "Gender_Label": "Gender", "Married_Label": "Married", "Education_Label": "Education",
            "Loan_Status_Label": "Loan_Status", ID_COLUMN: "Applicant_ID",
        }
    )
    return out


def main():
    df = pd.read_csv(FEATURED_DATA_PATH)
    df = add_model_predictions(df)
    df = add_decision_fields(df)
    dashboard_df = build_dashboard_dataset(df)
    dashboard_df.to_csv(POWERBI_DATA_PATH, index=False, encoding="utf-8-sig")

    print(f"Power BI dataset saved -> {POWERBI_DATA_PATH}")
    print(f"Rows: {len(dashboard_df)}, Columns: {len(dashboard_df.columns)}")
    print("\nApproval rate (actual):")
    print(dashboard_df["Loan_Status"].value_counts(normalize=True).round(3))
    print("\nRisk category distribution:")
    print(dashboard_df["Risk_Category"].value_counts())
    print("\nFinal decision distribution (model + affordability check):")
    print(dashboard_df["Final_Decision"].value_counts())


if __name__ == "__main__":
    main()
