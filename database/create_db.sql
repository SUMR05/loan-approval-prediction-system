-- ============================================================================
-- Loan Approval Prediction System - Database Schema
-- Engine: SQLite (portable, zero-config). The same DDL works on PostgreSQL/
-- MySQL with minor type tweaks (see notes below).
-- ============================================================================

DROP TABLE IF EXISTS loan_details;
DROP TABLE IF EXISTS credit_profile;
DROP TABLE IF EXISTS applicants;

-- Core applicant demographic/employment info
CREATE TABLE applicants (
    applicant_id        TEXT PRIMARY KEY,
    gender               TEXT,
    married              TEXT,
    dependents           TEXT,
    education            TEXT,
    self_employed        TEXT,
    employment_status    TEXT,
    years_at_current_job REAL,
    property_area        TEXT
);

-- Credit / risk profile, one-to-one with applicants
CREATE TABLE credit_profile (
    applicant_id     TEXT PRIMARY KEY REFERENCES applicants(applicant_id),
    credit_score     INTEGER,
    credit_history   INTEGER,      -- 1 = good history, 0 = poor/none
    existing_loans_count INTEGER,
    debt_to_income_ratio REAL
);

-- Loan application / financial details, one-to-one with applicants
CREATE TABLE loan_details (
    applicant_id        TEXT PRIMARY KEY REFERENCES applicants(applicant_id),
    applicant_income    REAL,
    coapplicant_income  REAL,
    loan_amount         REAL,      -- in thousands
    loan_amount_term    INTEGER,   -- in months
    loan_status         TEXT       -- 'Y' approved, 'N' rejected
);

CREATE INDEX idx_loan_status ON loan_details(loan_status);
CREATE INDEX idx_credit_score ON credit_profile(credit_score);
CREATE INDEX idx_property_area ON applicants(property_area);

-- Notes for production RDBMS (PostgreSQL/MySQL):
--   * TEXT -> VARCHAR(n) where a fixed max length makes sense
--   * Add NOT NULL / CHECK constraints once source data is fully validated
--   * Consider partitioning loan_details by application date at scale
