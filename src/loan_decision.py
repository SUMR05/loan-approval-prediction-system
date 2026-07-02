"""
Turns a raw ML approve/reject prediction into a business-usable loan decision:

    * Approved applicants get a maximum eligible loan amount, sized from
      income, credit band, and existing obligations (reverse-EMI calc) -
      the approved amount may be less than what was requested.
    * Rejected applicants get one or more concrete, human-readable reasons.

This mirrors how real lenders separate "is this applicant creditworthy"
(the ML model) from "how much can they actually afford to repay"
(an affordability/underwriting rule). All amounts are reported in rupees.
"""

import pandas as pd

ANNUAL_INTEREST_RATE = 0.10

# Share of monthly income a lender is willing to let go toward a new EMI,
# by credit-score band - higher score, higher affordable share.
AFFORDABILITY_BY_CREDIT_BAND = {
    "Poor": 0.20,
    "Fair": 0.35,
    "Good": 0.45,
    "Very Good": 0.50,
    "Excellent": 0.55,
}

# Below this fraction of the requested amount, a "partial approval" isn't
# meaningful to the applicant - treat it as a rejection instead.
MIN_VIABLE_APPROVAL_FRACTION = 0.15

# LoanAmount (and therefore the amounts computed here) is stored in
# thousands of rupees, e.g. LoanAmount = 120 means Rs 1,20,000.
THOUSAND = 1000


def format_inr(amount: float) -> str:
    """Formats a full rupee amount using Indian digit grouping, e.g. 1250000 -> '₹12,50,000'."""
    value = int(round(amount))
    sign = "-" if value < 0 else ""
    digits = str(abs(value))

    if len(digits) <= 3:
        grouped = digits
    else:
        last_three = digits[-3:]
        remaining = digits[:-3]
        parts = []
        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.insert(0, remaining)
        grouped = ",".join(parts) + "," + last_three

    return f"{sign}₹{grouped}"


def _affordability_ratio(row) -> float:
    base_ratio = AFFORDABILITY_BY_CREDIT_BAND.get(row.get("Credit_Score_Band"), 0.35)
    if row["Credit_History"] == 0:
        base_ratio *= 0.5
    existing_loans_penalty = min(row["Existing_Loans_Count"] * 0.05, 0.20)
    return max(base_ratio - existing_loans_penalty, 0.10)


def estimate_max_eligible_amount(row) -> float:
    """Maximum loan principal (in thousands of rupees, same unit as LoanAmount)
    the applicant could service, given an affordable monthly EMI."""
    affordable_emi = row["Total_Income"] * _affordability_ratio(row)
    term_months = int(row["Loan_Amount_Term"])
    if term_months <= 0 or affordable_emi <= 0:
        return 0.0

    r = ANNUAL_INTEREST_RATE / 12
    principal = affordable_emi * (((1 + r) ** term_months - 1) / (r * (1 + r) ** term_months))
    return round(max(principal / THOUSAND, 0.0), 1)


def _rejection_reasons(row, max_eligible_amount_k: float) -> list:
    reasons = []
    if row["Credit_History"] == 0:
        reasons.append("No established credit history")
    if row["Credit_Score"] < 580:
        reasons.append(f"Low credit score ({int(row['Credit_Score'])}), below the minimum threshold of 580")
    if row["Debt_To_Income_Ratio"] > 0.45:
        reasons.append(f"High debt-to-income ratio ({row['Debt_To_Income_Ratio']:.0%})")
    if row["Balance_Income"] < 0:
        reasons.append("Estimated loan installment exceeds the applicant's disposable income")
    if row.get("Employment_Status") == "Unemployed":
        reasons.append("Applicant is currently unemployed")
    if row["Existing_Loans_Count"] >= 3:
        reasons.append(f"High number of existing loan obligations ({int(row['Existing_Loans_Count'])})")
    if row["LoanAmount"] > max_eligible_amount_k:
        reasons.append(
            f"Requested amount ({format_inr(row['LoanAmount'] * THOUSAND)}) exceeds the maximum "
            f"eligible amount ({format_inr(max_eligible_amount_k * THOUSAND)}) based on income and repayment capacity"
        )
    if not reasons:
        reasons.append(
            "Overall risk profile is below the approval threshold based on combined "
            "credit, income, and repayment factors"
        )
    return reasons


def build_decision(row, ml_approved: bool) -> pd.Series:
    """Combines the ML creditworthiness prediction with an affordability
    check to produce a final decision, approved amount, and reason.
    Approved_Amount_INR / Max_Eligible_Amount_INR are full rupee values."""
    requested_k = row["LoanAmount"]
    max_eligible_k = estimate_max_eligible_amount(row)

    if not ml_approved:
        return pd.Series({
            "Max_Eligible_Amount_INR": round(max_eligible_k * THOUSAND),
            "Approved_Amount_INR": 0,
            "Final_Decision": "Rejected",
            "Decision_Reason": "; ".join(_rejection_reasons(row, max_eligible_k)),
        })

    approved_k = round(min(requested_k, max_eligible_k), 1)

    if approved_k < requested_k * MIN_VIABLE_APPROVAL_FRACTION:
        return pd.Series({
            "Max_Eligible_Amount_INR": round(max_eligible_k * THOUSAND),
            "Approved_Amount_INR": 0,
            "Final_Decision": "Rejected",
            "Decision_Reason": "; ".join(_rejection_reasons(row, max_eligible_k)),
        })

    if approved_k < requested_k:
        reason = (
            f"Approved for a reduced amount due to income-based affordability limits "
            f"(requested {format_inr(requested_k * THOUSAND)}, max eligible {format_inr(max_eligible_k * THOUSAND)})"
        )
        decision = "Partially Approved"
    else:
        reason = "Meets credit history, credit score, and income-based affordability requirements"
        decision = "Approved"

    return pd.Series({
        "Max_Eligible_Amount_INR": round(max_eligible_k * THOUSAND),
        "Approved_Amount_INR": round(approved_k * THOUSAND),
        "Final_Decision": decision,
        "Decision_Reason": reason,
    })
