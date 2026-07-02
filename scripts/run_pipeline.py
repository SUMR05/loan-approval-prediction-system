"""
Runs the full Loan Approval Prediction System pipeline end to end:

    1. Generate sample raw data        -> data/raw/loan_data.csv
    2. Clean / preprocess               -> data/processed/loan_data_cleaned.csv
    3. Load into SQLite + run SQL demo  -> database/loan_approval.db
    4. Feature engineering              -> data/processed/loan_data_features.csv
    5. Train & compare ML models        -> models/best_model.pkl + outputs/
    6. Predict sample new applicants    -> outputs/new_predictions.csv
    7. Build Power BI dataset           -> data/powerbi/loan_dashboard_data.csv

Usage:
    python scripts/run_pipeline.py
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import generate_sample_data
import data_preprocessing
import load_to_sql
import feature_engineering
import train_models
import predict
import generate_powerbi_data


def run_step(step_number: int, title: str, func) -> None:
    print("\n" + "=" * 78)
    print(f"STEP {step_number}: {title}")
    print("=" * 78)
    start = time.time()
    func()
    print(f"\n[Step {step_number} completed in {time.time() - start:.2f}s]")


def main():
    run_step(1, "Generating sample loan dataset", generate_sample_data.main)
    run_step(2, "Cleaning and preprocessing data", data_preprocessing.main)
    run_step(3, "Loading data into SQL database and running demo queries", load_to_sql.main)
    run_step(4, "Engineering features", feature_engineering.main)
    run_step(5, "Training and comparing ML models", train_models.main)
    run_step(6, "Scoring sample new applicants", predict.main)
    run_step(7, "Building Power BI dashboard dataset", generate_powerbi_data.main)

    print("\n" + "=" * 78)
    print("PIPELINE COMPLETE")
    print("=" * 78)
    print("Key outputs:")
    print("  models/best_model.pkl              - trained model ready to deploy")
    print("  outputs/model_comparison.csv       - metric comparison across models")
    print("  outputs/evaluation_report.txt      - full evaluation report")
    print("  outputs/confusion_matrices/        - confusion matrix plots per model")
    print("  outputs/new_predictions.csv        - predictions for sample new applicants")
    print("  data/powerbi/loan_dashboard_data.csv - Power BI-ready dataset")
    print("  database/loan_approval.db          - SQLite database")


if __name__ == "__main__":
    main()
