"""
Central configuration: file paths and column definitions shared across the
pipeline (preprocessing, feature engineering, training, prediction, Power BI
export). Keeping these in one place avoids column-name drift between stages.
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw", "loan_data.csv")
CLEANED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "loan_data_cleaned.csv")
FEATURED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "loan_data_features.csv")
POWERBI_DATA_PATH = os.path.join(BASE_DIR, "data", "powerbi", "loan_dashboard_data.csv")

DATABASE_PATH = os.path.join(BASE_DIR, "database", "loan_approval.db")
CREATE_DB_SQL_PATH = os.path.join(BASE_DIR, "database", "create_db.sql")

MODELS_DIR = os.path.join(BASE_DIR, "models")
BEST_MODEL_PATH = os.path.join(MODELS_DIR, "best_model.pkl")
PREPROCESSOR_PATH = os.path.join(MODELS_DIR, "preprocessor.pkl")
MODEL_METADATA_PATH = os.path.join(MODELS_DIR, "model_metadata.json")

OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
EVALUATION_REPORT_PATH = os.path.join(OUTPUTS_DIR, "evaluation_report.txt")
MODEL_COMPARISON_CSV = os.path.join(OUTPUTS_DIR, "model_comparison.csv")
CONFUSION_MATRIX_DIR = os.path.join(OUTPUTS_DIR, "confusion_matrices")

# ---------------------------------------------------------------------------
# Columns
# ---------------------------------------------------------------------------
ID_COLUMN = "Applicant_ID"
TARGET_COLUMN = "Loan_Status"

CATEGORICAL_COLUMNS = [
    "Gender",
    "Married",
    "Dependents",
    "Education",
    "Self_Employed",
    "Employment_Status",
    "Property_Area",
]

NUMERICAL_COLUMNS = [
    "ApplicantIncome",
    "CoapplicantIncome",
    "LoanAmount",
    "Loan_Amount_Term",
    "Credit_Score",
    "Credit_History",
    "Existing_Loans_Count",
    "Years_At_Current_Job",
    "Debt_To_Income_Ratio",
]

# Engineered features added on top of the raw/cleaned columns
ENGINEERED_NUMERICAL_COLUMNS = [
    "Total_Income",
    "Income_To_Loan_Ratio",
    "Loan_Amount_Per_Term",
    "EMI",
    "Balance_Income",
]

RANDOM_STATE = 42
TEST_SIZE = 0.2
