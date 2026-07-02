"""
Generates a synthetic loan applicant dataset for the Loan Approval Prediction System.

The dataset is built from realistic statistical distributions and a rule-based
approval score, with deliberately injected missing values and messy formatting
so the preprocessing step in data_preprocessing.py has real work to do.

Run directly to (re)create data/raw/loan_data.csv:
    python src/generate_sample_data.py
"""

import os
import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_APPLICANTS = 5000

RAW_DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "loan_data.csv")


def generate_loan_dataset(n_rows: int = N_APPLICANTS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    applicant_id = [f"APP{100000 + i}" for i in range(n_rows)]

    gender = rng.choice(["Male", "Female"], size=n_rows, p=[0.58, 0.42])
    married = rng.choice(["Yes", "No"], size=n_rows, p=[0.65, 0.35])
    dependents = rng.choice(["0", "1", "2", "3+"], size=n_rows, p=[0.55, 0.2, 0.15, 0.1])
    education = rng.choice(["Graduate", "Not Graduate"], size=n_rows, p=[0.78, 0.22])
    self_employed = rng.choice(["Yes", "No"], size=n_rows, p=[0.14, 0.86])
    employment_status = rng.choice(
        ["Salaried", "Self-Employed", "Business Owner", "Unemployed"],
        size=n_rows,
        p=[0.60, 0.18, 0.15, 0.07],
    )
    property_area = rng.choice(["Urban", "Semiurban", "Rural"], size=n_rows, p=[0.4, 0.38, 0.22])

    # Financial attributes ---------------------------------------------------
    applicant_income = rng.gamma(shape=4.5, scale=1400, size=n_rows).round(0) + 1500
    coapplicant_income = np.where(
        married == "Yes",
        rng.gamma(shape=2.5, scale=900, size=n_rows).round(0),
        0.0,
    )

    credit_score = rng.normal(loc=650, scale=90, size=n_rows).round(0)
    credit_score = np.clip(credit_score, 300, 850)

    credit_history = rng.choice([1, 0], size=n_rows, p=[0.84, 0.16])  # 1 = good history

    loan_amount = (rng.gamma(shape=3.0, scale=45, size=n_rows) + 20).round(0)  # in thousands
    loan_amount_term = rng.choice(
        [12, 36, 60, 84, 120, 180, 240, 300, 360],
        size=n_rows,
        p=[0.03, 0.07, 0.1, 0.1, 0.15, 0.15, 0.15, 0.1, 0.15],
    )

    existing_loans_count = rng.poisson(lam=0.6, size=n_rows)
    years_at_current_job = np.clip(rng.exponential(scale=4.0, size=n_rows), 0, 35).round(1)

    total_income = applicant_income + coapplicant_income
    debt_to_income_ratio = np.clip(
        (loan_amount * 1000 / (loan_amount_term / 12)) / (total_income * 12) * rng.normal(1, 0.15, n_rows),
        0.02,
        1.5,
    ).round(3)

    # Rule-based "true" approval likelihood (drives the target label) -------
    score = (
        0.0035 * (credit_score - 300)
        + 1.8 * credit_history
        - 2.2 * debt_to_income_ratio
        + 0.00006 * total_income
        - 0.004 * loan_amount
        + 0.15 * years_at_current_job
        - 0.35 * (employment_status == "Unemployed")
        + 0.15 * (education == "Graduate")
        - 0.25 * existing_loans_count
        + rng.normal(0, 0.9, n_rows)
    )
    approval_prob = 1 / (1 + np.exp(-(score - 2.2)))
    loan_status = np.where(rng.uniform(0, 1, n_rows) < approval_prob, "Y", "N")

    df = pd.DataFrame(
        {
            "Applicant_ID": applicant_id,
            "Gender": gender,
            "Married": married,
            "Dependents": dependents,
            "Education": education,
            "Self_Employed": self_employed,
            "Employment_Status": employment_status,
            "ApplicantIncome": applicant_income,
            "CoapplicantIncome": coapplicant_income,
            "LoanAmount": loan_amount,
            "Loan_Amount_Term": loan_amount_term,
            "Credit_Score": credit_score.astype(int),
            "Credit_History": credit_history,
            "Existing_Loans_Count": existing_loans_count,
            "Years_At_Current_Job": years_at_current_job,
            "Debt_To_Income_Ratio": debt_to_income_ratio,
            "Property_Area": property_area,
            "Loan_Status": loan_status,
        }
    )

    df = _inject_real_world_messiness(df, rng)
    return df


def _inject_real_world_messiness(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Randomly blanks out values and adds inconsistent formatting,
    mimicking a real intake dataset so downstream cleaning code is meaningful."""

    df = df.copy()
    n_rows = len(df)

    for col, frac in [
        ("Gender", 0.02),
        ("Married", 0.01),
        ("Dependents", 0.03),
        ("Self_Employed", 0.05),
        ("Credit_Score", 0.04),
        ("LoanAmount", 0.03),
        ("Loan_Amount_Term", 0.02),
        ("Credit_History", 0.06),
        ("Years_At_Current_Job", 0.02),
    ]:
        n_missing = int(n_rows * frac)
        idx = rng.choice(n_rows, size=n_missing, replace=False)
        df.loc[idx, col] = np.nan

    # Inconsistent casing / whitespace to demonstrate text cleaning
    messy_idx = rng.choice(n_rows, size=int(n_rows * 0.08), replace=False)
    df.loc[messy_idx, "Gender"] = df.loc[messy_idx, "Gender"].astype(str).str.lower()

    space_idx = rng.choice(n_rows, size=int(n_rows * 0.05), replace=False)
    df.loc[space_idx, "Property_Area"] = " " + df.loc[space_idx, "Property_Area"].astype(str) + " "

    # A few duplicate applicant records, as often happens with re-submissions
    dup_rows = df.sample(n=15, random_state=1)
    df = pd.concat([df, dup_rows], ignore_index=True)
    return df


def main():
    df = generate_loan_dataset()
    os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"Generated {len(df)} loan applicant records -> {RAW_DATA_PATH}")
    print(df["Loan_Status"].value_counts(normalize=True).rename("proportion"))


if __name__ == "__main__":
    main()
