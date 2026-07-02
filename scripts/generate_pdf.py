"""
Builds a simple, easy-to-read PDF overview of the Loan Approval Prediction
System - written in plain language for someone with basic knowledge, not
a data science background. Covers what the project does, how it works,
the models compared, the results, and the business outcome.

Pulls real numbers from outputs/model_comparison.csv and
models/model_metadata.json, so the PDF always reflects the last training
run - run train_models.py first if you want fresh numbers.

Run directly:
    python scripts/generate_pdf.py
"""

import json
import os

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    HRFlowable,
    ListFlowable,
    ListItem,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_COMPARISON_CSV = os.path.join(BASE_DIR, "outputs", "model_comparison.csv")
MODEL_METADATA_PATH = os.path.join(BASE_DIR, "models", "model_metadata.json")
CONFUSION_MATRIX_DIR = os.path.join(BASE_DIR, "outputs", "confusion_matrices")
OUTPUT_PDF = os.path.join(BASE_DIR, "outputs", "Loan_Approval_Prediction_System_Overview.pdf")

NAVY = colors.HexColor("#1F3864")
TEAL = colors.HexColor("#2E86AB")
GREEN = colors.HexColor("#E8F3EA")
GREEN_TEXT = colors.HexColor("#1B5E20")
GREY_TEXT = colors.HexColor("#333333")
LIGHT_BG = colors.HexColor("#F4F6F9")

styles = getSampleStyleSheet()

title_style = ParagraphStyle("TitleBig", parent=styles["Title"], fontSize=28, leading=34, textColor=NAVY, spaceAfter=16)
subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], fontSize=14, textColor=colors.HexColor("#555555"), spaceAfter=4, alignment=TA_CENTER)
h1_style = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=20, textColor=NAVY, spaceBefore=6, spaceAfter=10)
h2_style = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=15, textColor=TEAL, spaceBefore=10, spaceAfter=6)
body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=12.5, leading=18, textColor=GREY_TEXT, spaceAfter=6)
bullet_style = ParagraphStyle("Bullet", parent=body_style, leftIndent=14, spaceAfter=6)
caption_style = ParagraphStyle("Caption", parent=styles["Normal"], fontSize=10.5, alignment=TA_CENTER, textColor=NAVY, spaceBefore=4)


def para(text):
    return Paragraph(text, body_style)


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(item, bullet_style), bulletColor=TEAL) for item in items],
        bulletType="bullet",
        start="circle",
        leftIndent=16,
    )


def section(title, flowables):
    story = [Paragraph(title, h1_style)]
    story.extend(flowables)
    story.append(Spacer(1, 10))
    return story


def rule():
    return HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#CCCCCC"), spaceBefore=4, spaceAfter=14)


def main():
    comparison_df = pd.read_csv(MODEL_COMPARISON_CSV)
    with open(MODEL_METADATA_PATH, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    best_model = metadata["best_model"]
    best_metrics = metadata["metrics"]

    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        topMargin=0.9 * inch,
        bottomMargin=0.8 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
        title="Loan Approval Prediction System - Simple Overview",
    )

    story = []

    # ---- Cover ----
    story.append(Spacer(1, 1.6 * inch))
    story.append(Paragraph("Loan Approval Prediction System", title_style))
    story.append(Paragraph("A Simple, Easy-to-Understand Project Overview", subtitle_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Built with Python, SQL, Pandas, Scikit-learn, and Power BI", subtitle_style))
    story.append(Spacer(1, 2.2 * inch))
    story.append(Paragraph("This document explains the project in plain, simple language -", subtitle_style))
    story.append(Paragraph("no technical background needed to follow along.", subtitle_style))
    story.append(PageBreak())

    # ---- 1. What is this project ----
    story.extend(section(
        "1. What Is This Project?",
        [
            para(
                "This project looks at a loan applicant's details - like income, credit score, "
                "job status, and how much loan they want - and helps decide:"
            ),
            bullets([
                "Should the loan be <b>Approved</b> or <b>Rejected</b>?",
                "If approved, <b>how much money</b> should actually be given?",
                "If rejected, <b>what is the reason</b>, in plain words?",
            ]),
            Spacer(1, 4),
            para(
                "In short: it takes messy, real-world applicant data and turns it into a clear, "
                "explainable loan decision - the same way a bank would think about it, but automated."
            ),
        ],
    ))

    # ---- 2. How it works ----
    story.extend(section(
        "2. How It Works (Step by Step)",
        [
            para("Think of it like an assembly line. Each step improves the data a little more:"),
            bullets([
                "<b>Step 1 - Get the data:</b> A list of loan applicants and their details.",
                "<b>Step 2 - Clean the data:</b> Fix missing values, typos, and duplicate entries.",
                "<b>Step 3 - Store it in SQL:</b> Organize the data so it can be searched easily.",
                "<b>Step 4 - Create useful new info:</b> Like monthly EMI, or income left after EMI.",
                "<b>Step 5 - Train the model:</b> Show the computer thousands of past examples so it learns the pattern.",
                "<b>Step 6 - Test the model:</b> Check how good its guesses are.",
                "<b>Step 7 - Pick the best model:</b> Out of 3 models tried, keep the one that guessed best.",
                "<b>Step 8 - Save the model:</b> So it can be reused without retraining every time.",
                "<b>Step 9 - Predict new applicants:</b> Feed in a new person's details, get a decision.",
                "<b>Step 10 - Send data to Power BI:</b> So managers can see charts, not just numbers.",
            ]),
        ],
    ))
    story.append(PageBreak())

    # ---- 3. Tech stack ----
    story.extend(section(
        "3. Tools Used (In Simple Words)",
        [
            bullets([
                "<b>Python</b> - the programming language used to clean data and build the model.",
                "<b>Pandas</b> - a tool for organizing data, like a smart spreadsheet inside Python.",
                "<b>SQL (SQLite)</b> - stores the applicant data so it can be searched and filtered, like a filing cabinet.",
                "<b>Scikit-learn</b> - the library used to train and compare machine learning models.",
                "<b>Power BI</b> - turns the results into charts and dashboards for business people to view.",
            ]),
        ],
    ))

    # ---- 4. What is ML ----
    story.extend(section(
        "4. What Is \"Machine Learning\" Doing Here?",
        [
            para(
                "Imagine showing a child 1,000 old loan applications, and for each one telling them "
                "\"this got approved\" or \"this got rejected.\" After seeing enough examples, the child "
                "starts noticing patterns - like \"people with bad credit history usually get rejected.\""
            ),
            para(
                "That is exactly what the model does. It studies thousands of past examples, learns the "
                "pattern, and then uses that pattern to guess the outcome for a brand-new applicant it has "
                "never seen before."
            ),
        ],
    ))

    # ---- 5. Dataset ----
    story.extend(section(
        "5. About the Data",
        [
            bullets([
                "5,000 sample loan applicant records were used.",
                "Details included: Gender, Marital Status, Education, Employment Status, Income.",
                "Also included: Loan Amount, Loan Term, Credit Score, Credit History, Existing Loans.",
                "The answer column: Loan Status - Approved or Rejected.",
                "The data was made realistic on purpose - with missing values, duplicate entries, and "
                "messy text - just like real bank data.",
            ]),
        ],
    ))
    story.append(PageBreak())

    # ---- 6. Cleaning & features ----
    story.extend(section(
        "6. Cleaning the Data & Creating Useful Info",
        [
            Paragraph("Cleaning the data:", h2_style),
            bullets([
                "Filled in missing values (most common value for categories, middle value for numbers).",
                "Fixed inconsistent text, like extra spaces or mixed capital/small letters.",
                "Removed duplicate applications.",
                "Fixed values that were clearly out of a normal range.",
            ]),
            Paragraph("New useful columns created:", h2_style),
            bullets([
                "<b>Total Income</b> - applicant's income plus co-applicant's income.",
                "<b>EMI</b> - the estimated monthly loan payment.",
                "<b>Balance Income</b> - how much income is left after paying the EMI.",
                "<b>Debt-to-Income Ratio</b> - how much of the income already goes toward debt.",
                "<b>Risk Category</b> - a simple label: Low, Medium, or High risk.",
            ]),
        ],
    ))

    # ---- 7. Models compared ----
    story.extend(section(
        "7. The 3 Models Compared",
        [
            bullets([
                "<b>Logistic Regression</b> - the simplest method. It looks at each factor (income, "
                "credit score, etc.), gives it a weight, and adds everything up to decide. Easy to explain.",
                "<b>Decision Tree</b> - works like a flowchart of yes/no questions. \"Is credit history "
                "good? -> Yes -> Is income above a limit? -> Yes -> Approve.\"",
                "<b>Random Forest</b> - instead of one flowchart, it builds many flowcharts and lets them "
                "vote. Usually stronger, but harder to explain simply.",
            ]),
            para("All three were trained and tested on the exact same data, so the comparison is fair."),
        ],
    ))
    story.append(PageBreak())

    # ---- 8. Results table ----
    story.append(Paragraph("8. Results - Which Model Won?", h1_style))
    story.append(para(
        "Each model was scored using 4 simple checks: Accuracy, Precision, Recall, and F1-Score "
        "(explained below the table)."
    ))
    story.append(Spacer(1, 8))

    table_data = [["Model", "Accuracy", "Precision", "Recall", "F1-Score"]]
    best_row_idx = None
    for i, r in comparison_df.iterrows():
        table_data.append([r["model"], f"{r['accuracy']:.2f}", f"{r['precision']:.2f}", f"{r['recall']:.2f}", f"{r['f1_score']:.2f}"])
        if r["model"] == best_model:
            best_row_idx = i + 1  # +1 for header row

    result_table = Table(table_data, colWidths=[1.9 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch, 1.1 * inch])
    table_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11.5),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]
    if best_row_idx is not None:
        table_style_cmds.append(("BACKGROUND", (0, best_row_idx), (-1, best_row_idx), GREEN))
        table_style_cmds.append(("TEXTCOLOR", (0, best_row_idx), (-1, best_row_idx), GREEN_TEXT))
        table_style_cmds.append(("FONTNAME", (0, best_row_idx), (-1, best_row_idx), "Helvetica-Bold"))
    result_table.setStyle(TableStyle(table_style_cmds))
    story.append(result_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"(Green row = the winning model: {best_model})", caption_style))
    story.append(Spacer(1, 16))

    story.append(Paragraph("What do these words mean?", h2_style))
    story.append(bullets([
        "<b>Accuracy</b> - out of 100 guesses, how many were correct overall?",
        "<b>Precision</b> - out of everyone the model said \"approve,\" how many really deserved it? "
        "(Are we being too generous?)",
        "<b>Recall</b> - out of everyone who really deserved approval, how many did the model catch? "
        "(Are we rejecting good people by mistake?)",
        "<b>F1-Score</b> - one single number that balances Precision and Recall together.",
    ]))
    story.append(Spacer(1, 6))
    story.append(para(
        f"<b>{best_model}</b> was chosen as the best model because it had the highest F1-Score "
        f"({best_metrics['f1_score']:.0%}) - meaning it best balanced approving good applicants and "
        f"catching risky ones."
    ))
    story.append(PageBreak())

    # ---- 9. Confusion matrices ----
    story.append(Paragraph("9. How Right or Wrong Was Each Model?", h1_style))
    story.append(para(
        "A \"confusion matrix\" is a simple picture that shows how many predictions were correct and "
        "how many were wrong, for each model."
    ))
    story.append(Spacer(1, 8))

    cm_files = [
        ("confusion_matrix_logistic_regression.png", "Logistic Regression"),
        ("confusion_matrix_decision_tree.png", "Decision Tree"),
        ("confusion_matrix_random_forest.png", "Random Forest"),
    ]
    for filename, label in cm_files:
        path = os.path.join(CONFUSION_MATRIX_DIR, filename)
        if os.path.exists(path):
            story.append(Image(path, width=3.3 * inch, height=2.7 * inch))
            story.append(Paragraph(label, caption_style))
            story.append(Spacer(1, 10))
    story.append(PageBreak())

    # ---- 10. Decision logic ----
    story.extend(section(
        "10. How the Final Decision Is Made",
        [
            para("The model alone only says \"approve\" or \"reject.\" That's not enough for a real bank, "
                 "so a second, simple step was added:"),
            bullets([
                "<b>Step 1:</b> The model predicts if the applicant is trustworthy (Approve / Reject).",
                "<b>Step 2:</b> A simple rule checks how much loan the applicant can actually afford, "
                "based on their income.",
                "<b>Result:</b> Approved (full amount), Partially Approved (smaller amount), or Rejected.",
                "If rejected, the system lists the real reasons - low credit score, high debt, "
                "unemployment, too many existing loans, etc. - instead of just saying \"no.\"",
                "All loan amounts are shown in Rupees, for example: Rs 1,20,000.",
            ]),
        ],
    ))

    # ---- 11. Power BI ----
    story.extend(section(
        "11. The Power BI Dashboard",
        [
            para("All the results are also saved into one clean file that Power BI can open directly. "
                 "The dashboard shows:"),
            bullets([
                "Approval rate and Rejection rate",
                "Risk category breakdown (Low / Medium / High)",
                "Credit score analysis",
                "Income analysis",
                "Loan amount trends (requested vs. approved)",
                "Applicant profile summary",
            ]),
            para("This lets managers and business teams explore the results visually, without touching any code."),
        ],
    ))
    story.append(PageBreak())

    # ---- 12. Business insights ----
    story.extend(section(
        "12. What Did We Learn? (Business Insights)",
        [
            bullets([
                "Credit history is the single strongest sign of whether a loan gets approved.",
                "A high debt-to-income ratio often leads to rejection, even for small loan amounts.",
                "Unemployed applicants are rejected more often, even with similar income to others.",
                "The affordability check catches cases where a good applicant asks for more money than "
                "they can actually repay.",
            ]),
        ],
    ))

    # ---- 13. Conclusion ----
    story.extend(section(
        "13. Conclusion",
        [
            bullets([
                "A complete, working loan approval system was built - from raw data to final decision.",
                "Three machine learning models were compared, and the best one was chosen fairly.",
                f"The winning model, <b>{best_model}</b>, correctly predicts loan outcomes "
                f"{best_metrics['accuracy']:.0%} of the time on new data it has never seen.",
                "A real-world decision layer was added: approved amount + rejection reason, not just yes/no.",
                "A live Power BI dashboard was delivered for business reporting.",
                "The whole system is saved and ready to reuse - no need to retrain from scratch each time.",
            ]),
        ],
    ))
    story.append(rule())
    story.append(Paragraph(
        "This project shows how a real lending decision can be automated end-to-end - "
        "combining data cleaning, machine learning, business rules, and reporting into one simple system.",
        ParagraphStyle("Closing", parent=body_style, alignment=TA_CENTER, textColor=NAVY, fontSize=13),
    ))

    doc.build(story)
    print(f"PDF saved -> {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
