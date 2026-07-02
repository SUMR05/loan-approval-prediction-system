"""
Loads the cleaned applicant CSV into a normalized SQLite database
(database/loan_approval.db) using the schema in database/create_db.sql,
then runs the demonstration queries in database/queries.sql and prints
a preview of each result so SQL extraction/joins/aggregation can be
verified without a separate SQL client.

Run directly:
    python src/load_to_sql.py
"""

import sqlite3

import pandas as pd

from config import CLEANED_DATA_PATH, DATABASE_PATH, CREATE_DB_SQL_PATH


def build_schema(conn: sqlite3.Connection) -> None:
    with open(CREATE_DB_SQL_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)


def load_tables(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    applicants = df.rename(columns={"Applicant_ID": "applicant_id"})[
        [
            "applicant_id", "Gender", "Married", "Dependents", "Education",
            "Self_Employed", "Employment_Status", "Years_At_Current_Job", "Property_Area",
        ]
    ].rename(
        columns={
            "Gender": "gender", "Married": "married", "Dependents": "dependents",
            "Education": "education", "Self_Employed": "self_employed",
            "Employment_Status": "employment_status",
            "Years_At_Current_Job": "years_at_current_job", "Property_Area": "property_area",
        }
    )

    credit_profile = df.rename(columns={"Applicant_ID": "applicant_id"})[
        ["applicant_id", "Credit_Score", "Credit_History", "Existing_Loans_Count", "Debt_To_Income_Ratio"]
    ].rename(
        columns={
            "Credit_Score": "credit_score", "Credit_History": "credit_history",
            "Existing_Loans_Count": "existing_loans_count",
            "Debt_To_Income_Ratio": "debt_to_income_ratio",
        }
    )

    loan_details = df.rename(columns={"Applicant_ID": "applicant_id"})[
        [
            "applicant_id", "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
            "Loan_Amount_Term", "Loan_Status",
        ]
    ].rename(
        columns={
            "ApplicantIncome": "applicant_income", "CoapplicantIncome": "coapplicant_income",
            "LoanAmount": "loan_amount", "Loan_Amount_Term": "loan_amount_term",
            "Loan_Status": "loan_status",
        }
    )

    applicants.to_sql("applicants", conn, if_exists="append", index=False)
    credit_profile.to_sql("credit_profile", conn, if_exists="append", index=False)
    loan_details.to_sql("loan_details", conn, if_exists="append", index=False)


def run_demo_queries(conn: sqlite3.Connection) -> None:
    print("\n--- Approval vs Rejection rate ---")
    print(pd.read_sql_query(
        "SELECT loan_status, COUNT(*) AS applicant_count FROM loan_details GROUP BY loan_status", conn
    ))

    print("\n--- Approval rate by employment status ---")
    print(pd.read_sql_query(
        """
        SELECT a.employment_status,
               COUNT(*) AS total_applicants,
               ROUND(100.0 * SUM(CASE WHEN l.loan_status = 'Y' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate_pct
        FROM applicants a
        JOIN loan_details l ON a.applicant_id = l.applicant_id
        GROUP BY a.employment_status
        ORDER BY approval_rate_pct DESC
        """,
        conn,
    ))


def main():
    df = pd.read_csv(CLEANED_DATA_PATH)

    conn = sqlite3.connect(DATABASE_PATH)
    try:
        build_schema(conn)
        load_tables(conn, df)
        conn.commit()
        print(f"Loaded {len(df)} applicant records into {DATABASE_PATH}")
        run_demo_queries(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
