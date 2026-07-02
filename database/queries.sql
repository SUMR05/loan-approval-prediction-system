-- ============================================================================
-- Loan Approval Prediction System - Analysis Queries
-- Run against database/loan_approval.db (created by src/load_to_sql.py)
-- These demonstrate filtering, joins, and aggregation for applicant records,
-- and double as the source logic for several Power BI dashboard fields.
-- ============================================================================

-- 1. Overall approval vs rejection rate
SELECT
    loan_status,
    COUNT(*) AS applicant_count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM loan_details), 2) AS pct_of_total
FROM loan_details
GROUP BY loan_status;

-- 2. Approval rate by employment status (join applicants + loan_details)
SELECT
    a.employment_status,
    COUNT(*) AS total_applicants,
    SUM(CASE WHEN l.loan_status = 'Y' THEN 1 ELSE 0 END) AS approved,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status = 'Y' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate_pct
FROM applicants a
JOIN loan_details l ON a.applicant_id = l.applicant_id
GROUP BY a.employment_status
ORDER BY approval_rate_pct DESC;

-- 3. Credit score analysis: average score and approval rate by credit-score band
SELECT
    CASE
        WHEN c.credit_score < 580 THEN 'Poor (<580)'
        WHEN c.credit_score < 670 THEN 'Fair (580-669)'
        WHEN c.credit_score < 740 THEN 'Good (670-739)'
        WHEN c.credit_score < 800 THEN 'Very Good (740-799)'
        ELSE 'Excellent (800+)'
    END AS credit_band,
    COUNT(*) AS applicants,
    ROUND(AVG(c.credit_score), 0) AS avg_credit_score,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status = 'Y' THEN 1 ELSE 0 END) / COUNT(*), 2) AS approval_rate_pct
FROM credit_profile c
JOIN loan_details l ON c.applicant_id = l.applicant_id
WHERE c.credit_score IS NOT NULL
GROUP BY credit_band
ORDER BY avg_credit_score;

-- 4. Income analysis: applicants with combined income above the portfolio median
SELECT a.applicant_id, a.employment_status, l.applicant_income, l.coapplicant_income,
       (l.applicant_income + l.coapplicant_income) AS total_income, l.loan_status
FROM applicants a
JOIN loan_details l ON a.applicant_id = l.applicant_id
WHERE (l.applicant_income + l.coapplicant_income) > (
    SELECT AVG(applicant_income + coapplicant_income) FROM loan_details
)
ORDER BY total_income DESC
LIMIT 50;

-- 5. Loan amount trends by property area
SELECT
    a.property_area,
    COUNT(*) AS applicants,
    ROUND(AVG(l.loan_amount), 1) AS avg_loan_amount_k,
    ROUND(MIN(l.loan_amount), 1) AS min_loan_amount_k,
    ROUND(MAX(l.loan_amount), 1) AS max_loan_amount_k
FROM applicants a
JOIN loan_details l ON a.applicant_id = l.applicant_id
GROUP BY a.property_area
ORDER BY avg_loan_amount_k DESC;

-- 6. High-risk applicants: poor/no credit history AND high debt-to-income ratio
SELECT a.applicant_id, a.employment_status, c.credit_score, c.credit_history,
       c.debt_to_income_ratio, l.loan_amount, l.loan_status
FROM applicants a
JOIN credit_profile c ON a.applicant_id = c.applicant_id
JOIN loan_details l ON a.applicant_id = l.applicant_id
WHERE c.credit_history = 0
  AND c.debt_to_income_ratio > 0.4
ORDER BY c.debt_to_income_ratio DESC;

-- 7. Rejection rate by number of existing loans (risk factor stacking)
SELECT
    c.existing_loans_count,
    COUNT(*) AS applicants,
    ROUND(100.0 * SUM(CASE WHEN l.loan_status = 'N' THEN 1 ELSE 0 END) / COUNT(*), 2) AS rejection_rate_pct
FROM credit_profile c
JOIN loan_details l ON c.applicant_id = l.applicant_id
GROUP BY c.existing_loans_count
ORDER BY c.existing_loans_count;

-- 8. Applicant profile summary (used for the Power BI "Applicant Profile" table)
SELECT
    a.applicant_id, a.gender, a.married, a.dependents, a.education,
    a.employment_status, a.property_area, c.credit_score, c.credit_history,
    l.applicant_income, l.coapplicant_income, l.loan_amount, l.loan_status
FROM applicants a
JOIN credit_profile c ON a.applicant_id = c.applicant_id
JOIN loan_details l ON a.applicant_id = l.applicant_id;
