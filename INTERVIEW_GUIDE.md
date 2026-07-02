# Loan Approval Prediction System — Interview Guide

A complete, self-contained reference for explaining this project in an
interview: what it does, what every folder/file is for, how data flows
through the pipeline, the actual results produced, and a bank of sample
Q&A. Read top to bottom once, then use the Q&A section to rehearse.

---

## 1. The 30-second pitch

"I built an end-to-end loan approval prediction system — Python for data
cleaning and modeling, SQL for the data layer, Scikit-learn for
classification, and Power BI for reporting. It takes applicant financial
data, engineers risk features like debt-to-income and balance income,
trains and compares three classification models, and produces a real
lending decision: not just approve/reject, but *how much* to approve
(which can be less than requested) or a plain-language reason for
rejection. Everything is reported in rupees and ships as a deployable
model plus a live Power BI dashboard."

---

## 2. What the system actually does (end to end)

1. Generates/ingests applicant data (income, credit history, employment,
   loan amount, loan term, credit score, existing loans, etc.)
2. Cleans it (missing values, inconsistent text, duplicates)
3. Loads it into a normalized SQL database for analyst-style querying
4. Engineers financial risk features (EMI, balance income, DTI, risk
   category)
5. Trains three ML classifiers and picks the best one by F1-score
6. Turns the ML approve/reject signal into a **business decision**:
   Approved / Partially Approved / Rejected, with a rupee amount and a
   reason
7. Publishes a Power BI-ready dataset for portfolio-level reporting

---

## 3. Complete folder-by-folder walkthrough

```
loan-approval-prediction-system/
├── data/
├── database/
├── src/
├── models/
├── outputs/
├── scripts/
├── requirements.txt
└── README.md
```

### `data/` — every stage of the data as it moves through the pipeline

| File | What it is | How to talk about it |
|---|---|---|
| `data/raw/loan_data.csv` | 5,000 synthetic applicant records with realistic distributions, injected missing values, inconsistent casing, and a handful of duplicate submissions | "I generated this synthetically so the cleaning step has genuine, realistic work to do — real intake data always has this kind of mess." |
| `data/raw/new_applicants_sample.csv` | A handful of example new applicants (no `Loan_Status`) used to demonstrate scoring | "This simulates the moment a real applicant walks in — the system has never seen them before." |
| `data/processed/loan_data_cleaned.csv` | Output of `data_preprocessing.py` — missing values imputed, text normalized, duplicates removed | "This is the single source of truth used by both the SQL load and the feature engineering step." |
| `data/processed/loan_data_features.csv` | Output of `feature_engineering.py` — cleaned data plus derived features and one-hot encoding, model-ready | "This is exactly what gets fed into `train_test_split`." |
| `data/powerbi/loan_dashboard_data.csv` | Flat, denormalized file combining features, actual outcomes, and predicted decisions — built for Power BI import | "One file, no joins needed, ready for `Get Data → Text/CSV`." |

### `database/` — the SQL layer

| File | What it is |
|---|---|
| `create_db.sql` | DDL for 3 normalized tables: `applicants`, `credit_profile`, `loan_details`, joined on `applicant_id`, with indexes on `loan_status`, `credit_score`, `property_area` |
| `queries.sql` | 8 standalone queries: approval/rejection rate, approval rate by employment status (JOIN), credit-score-band analysis, above-median income filter, loan amount trends by property area, high-risk applicant flag (multi-table JOIN), rejection rate by existing-loan count, and a full applicant-profile view |
| `loan_approval.db` | The actual SQLite database, built automatically by `src/load_to_sql.py` |

**Why SQLite and not Postgres/MySQL?** "Zero setup — no server to install — which makes the project runnable on any machine in one command. The DDL is portable; swapping to Postgres/MySQL only needs minor type tweaks (`TEXT` → `VARCHAR(n)`), which I noted directly in the schema file."

### `src/` — all the Python logic, one responsibility per file

| File | Responsibility | Key thing to mention |
|---|---|---|
| `config.py` | Single source of truth for file paths and column names | "Prevents column-name drift between preprocessing, training, and prediction — change a path once, not in six files." |
| `generate_sample_data.py` | Builds the synthetic raw dataset from statistical distributions plus a rule-based approval likelihood | "The approval label isn't random — it's driven by a logistic function of credit score, DTI, income, and employment, so the ML models have real signal to learn." |
| `data_preprocessing.py` | Cleans text, removes duplicates, imputes missing values (mode for categorical, median for numeric), clips out-of-range values, and **persists the exact imputation values to `models/impute_values.json`** | "That persistence matters — a new applicant scored six months from now gets the same fill values as training data, not silently different ones." |
| `load_to_sql.py` | Builds the SQLite schema and loads the cleaned CSV into it; runs two demo queries on load | "This is the bridge between the Python cleaning step and the SQL analysis layer." |
| `feature_engineering.py` | Derives `Total_Income`, `EMI`, `Balance_Income`, `Income_To_Loan_Ratio`, `Risk_Category` (Low/Medium/High), `Income_Bracket`, `Credit_Score_Band`; one-hot encodes categoricals | "`Risk_Category` is deliberately excluded from the model's training features — it's a business-rule summary of the same signals the model already sees, so feeding it back in would be circular, not genuinely new information." |
| `model_evaluation.py` | Reusable metric computation, confusion-matrix plotting, and text-report building | "Shared by `train_models.py` so the evaluation logic isn't duplicated per model." |
| `train_models.py` | Trains Logistic Regression, Decision Tree, and Random Forest through a shared `ColumnTransformer` (scaling for linear model, passthrough for one-hot columns); evaluates each on Accuracy/Precision/Recall/F1; selects the best by F1; saves model + preprocessor + metadata | "I used a stratified train/test split (80/20) to preserve the approval ratio, and selected the winning model on F1 rather than accuracy." |
| `loan_decision.py` | Converts the ML approve/reject signal into a real lending decision: sizes an affordable loan amount via reverse-EMI, and generates plain-language rejection reasons | "This is the layer that makes the system usable by a loan officer, not just a data scientist." |
| `predict.py` | CLI: takes a CSV of new applicants, runs the identical cleaning → feature engineering → prediction → decision pipeline, writes results and prints a per-applicant summary | "Deliberately standalone from the training code — this is what would sit behind an API in production." |
| `generate_powerbi_data.py` | Runs the saved model over the full historical dataset and builds the flat Power BI CSV, including both actual and predicted/decisioned outcomes | "Lets a BI analyst see model performance and portfolio risk trends without touching Python." |

### `models/` — everything needed to serve predictions without retraining

| File | What it is |
|---|---|
| `best_model.pkl` | The winning classifier (currently Logistic Regression), serialized with `joblib` |
| `preprocessor.pkl` | The fitted `ColumnTransformer` + the exact list of feature columns used at train time, bundled together |
| `impute_values.json` | The mode/median values used for missing-value imputation, so new applicants are cleaned identically to training data |
| `model_metadata.json` | Which model won, its metrics, feature list, train/test row counts, random seed — a paper trail for the deployed model |

**Why save the preprocessor separately from the model?** "Because a raw pickle of just the classifier isn't deployable — you also need the exact scaling and column order it was trained on. Bundling them together means `predict.py` and `generate_powerbi_data.py` can never silently drift out of sync with training."

### `outputs/` — everything produced by evaluation and prediction runs

| File | What it is |
|---|---|
| `model_comparison.csv` | Accuracy/Precision/Recall/F1 for all three models side by side |
| `evaluation_report.txt` | Full text report: per-model metrics plus `sklearn.classification_report` |
| `confusion_matrices/*.png` | One confusion matrix heatmap per model |
| `new_predictions.csv` | Output of the last `predict.py` run — decision, approved amount, reason per applicant |

### `scripts/run_pipeline.py`

Runs all seven stages — generate data → clean → load to SQL → engineer
features → train/compare/select model → score sample applicants → build
Power BI dataset — in order, with per-step timing and a summary of
outputs at the end. "This is the single command that proves the whole
thing works end to end, which is what I'd run in a demo or in CI."

### `requirements.txt` / `README.md`

Pinned dependencies (pandas, numpy, scikit-learn, matplotlib, seaborn,
joblib) and the full setup/run/architecture documentation.

---

## 4. The two-layer decision design (the most interesting part to explain)

This is worth walking through carefully because it shows system design
thinking beyond "train a model":

**Layer 1 — Creditworthiness (ML):** Logistic Regression predicts
approve/reject from credit score, income, DTI, employment, etc.

**Layer 2 — Affordability (business rule, `loan_decision.py`):** Even an
applicant the model approves might be requesting more than they can
actually repay. So a reverse-EMI calculation sizes the **maximum eligible
loan amount** from their income, credit-score band (higher band → higher
affordable share of income toward EMI), and existing loan obligations
(penalizes affordability further).

**Combining them:**
- ML says reject → **Rejected**, with stacked reasons (poor credit
  history, low credit score, high DTI, negative balance income,
  unemployment, too many existing loans, or amount exceeding what's
  affordable)
- ML says approve, but requested amount > affordable amount →
  **Partially Approved** for the affordable amount, with the reason shown
- ML says approve, and requested ≤ affordable → **Approved** in full
- If the affordable amount is below 15% of what was requested, a "token"
  partial approval isn't meaningful, so it's downgraded to **Rejected**

"Why not just have the model predict everything end-to-end?" — "Because
the dataset only has a binary approved/rejected label, not an 'amount
approved' label to regress on. Rather than fabricate a fake regression
target, I used a transparent, auditable underwriting rule for sizing —
which is also exactly how real lenders separate credit risk scoring from
affordability underwriting."

---

## 5. Actual results from this project

| Model | Accuracy | Precision | Recall | F1-score |
|---|---|---|---|---|
| **Logistic Regression (selected)** | 0.726 | 0.732 | 0.875 | **0.797** |
| Random Forest | 0.706 | 0.709 | 0.884 | 0.787 |
| Decision Tree | 0.693 | 0.717 | 0.826 | 0.768 |

- Trained on 4,000 rows, tested on 1,000 (stratified 80/20 split, `random_state=42`)
- 29 input features after encoding (numeric + engineered + one-hot categoricals)
- Full-dataset decision breakdown (5,000 applicants, using the trained model): **3,018 Approved, 690 Partially Approved, 1,292 Rejected**
- Risk category split: **1,943 High / 1,641 Medium / 1,416 Low**

**Talking point on the result itself:** "Logistic Regression narrowly beat
Random Forest. That's a legitimate finding, not a letdown — it suggests
the engineered features (EMI, balance income, DTI) already captured most
of the non-linear risk signal, so a linear model on top of good features
performs about as well as an ensemble. That's a useful thing to notice in
practice: feature engineering can substitute for model complexity."

---

## 6. Business insights (for the "what was the impact" question)

1. **Credit history is the single strongest predictor** — applicants with
   no/poor credit history are rejected at a dramatically higher rate
   regardless of income.
2. **Debt-to-income ratio matters more than raw loan amount** — a modest
   loan can still be rejected if it's unaffordable relative to income.
3. **Employment stability adds signal beyond income** — unemployed
   applicants are rejected more often even at comparable income levels.
4. **The affordability layer catches cases the ML model alone would miss**
   — a creditworthy applicant requesting an unaffordable amount gets
   right-sized instead of a blanket approval or rejection.

---

## 7. Sample interview questions and answers

**Q: Walk me through your project in two minutes.**
> A: Use the 30-second pitch (Section 1), then briefly narrate Section 2's
> seven steps in one sentence each.

**Q: Why did you choose F1-score to select the best model instead of accuracy?**
> A: "Loan decisions have asymmetric costs — approving a bad-credit
> applicant (a false positive) and rejecting a good one (a false negative)
> are both costly, in different ways. Accuracy treats all errors equally
> and can look good on an imbalanced dataset even if it's failing one
> class. F1 balances precision and recall, so I used it as the selection
> criterion, though I still reported all four metrics for transparency."

**Q: Why did Logistic Regression outperform Random Forest here?**
> A: "Because the engineered features — EMI, balance income, DTI — already
> encode most of the non-linear risk interactions that a tree ensemble
> would otherwise have to discover on its own. Once that work is done in
> feature engineering, a linear model can separate the classes almost as
> well. It's a reminder that model complexity isn't a substitute for good
> features."

**Q: How did you handle missing data, and how do you make sure new applicants are treated consistently?**
> A: "Categorical columns get mode imputation, numeric columns get median
> imputation — median because income and loan amounts are skewed and
> median is robust to outliers. Critically, I don't recompute those fill
> values at prediction time; I persist the exact values used during
> training to `models/impute_values.json` and reuse them, so a new
> applicant scored later isn't cleaned against a different, silently
> drifting statistic."

**Q: How do you prevent data leakage in your feature engineering?**
> A: "`Risk_Category` is a rule-based label built from credit score,
> credit history, DTI, and balance income — the same signals the model
> already receives as separate features. I deliberately excluded it from
> the training feature set, because including it would let the model see
> a compressed version of its own inputs relabeled as a new 'feature,'
> which inflates apparent performance without adding real information."

**Q: What happens when you score a new applicant whose category (e.g. property area) wasn't in the training set, or is missing from a small batch?**
> A: "The one-hot encoding is fit once during training and saved. At
> prediction time, I reindex the new applicant's feature row against the
> exact saved column list, filling any missing dummy columns with 0. So a
> small batch missing, say, 'Rural' applicants doesn't break the column
> alignment the model expects."

**Q: How would you deploy this in production?**
> A: "`predict.py` is already decoupled from training — it loads the saved
> model and preprocessor and exposes a clear input/output contract. I'd
> wrap that logic in a REST endpoint, add request validation, log
> predictions for monitoring, and set up scheduled retraining with drift
> detection on the input feature distributions."

**Q: Why compute an 'approved amount' instead of just approve/reject?**
> A: "Because a binary decision doesn't match how lending actually works —
> a creditworthy applicant can still request more than they can service.
> I added an affordability layer that reverse-calculates the maximum
> loan principal an applicant's income supports at a given term and rate,
> scaled by their credit band. If the requested amount exceeds that, they
> get a partial approval instead of a flat rejection, with the reasoning
> shown."

**Q: What's the reasoning behind your risk-category thresholds and affordability ratios?**
> A: "They mirror common underwriting heuristics — for example, a
> 45% debt-to-income ratio is a widely used cutoff in real lending, and I
> scaled the 'affordable share of income' up for stronger credit bands and
> down for more existing obligations. They're configurable constants at
> the top of `loan_decision.py`, not hardcoded inline, specifically so a
> credit policy team could tune them without touching the ML code."

**Q: What would you improve if you had more time?**
> A: "Three things: (1) replace the synthetic dataset with real historical
> loan outcomes and re-validate the model's assumptions; (2) add proper
> hyperparameter tuning (I used reasonable defaults, not a grid search);
> (3) add model monitoring for feature drift, since underwriting policy
> and applicant demographics shift over time."

**Q: How does the SQL layer fit in — why not just do everything in Pandas?**
> A: "The SQL layer exists because a real lending organization has data
> analysts and BI teams who query the applicant database directly, without
> touching the ML pipeline. Modeling it as normalized tables — applicants,
> credit_profile, loan_details — mirrors how this would actually be stored
> and queried in production, and the join/aggregation queries in
> `queries.sql` are the kind of ad hoc reporting an analyst would run."

**Q: What does the Power BI dataset let a business user do that the model alone doesn't?**
> A: "Monitor portfolio-level trends without running Python — approval
> rate over time, risk-category mix, requested vs. approved loan amounts,
> credit score distribution. It's a single flat file so there's no join
> logic needed inside Power BI itself."

---

## 8. Quick-reference cheat sheet (glance at this right before the interview)

- **Stack:** Python, Pandas, Scikit-learn, SQLite/SQL, Power BI
- **Dataset:** 5,000 synthetic applicants, realistic messiness injected
- **Models compared:** Logistic Regression, Decision Tree, Random Forest
- **Winner:** Logistic Regression — Accuracy 0.726, Precision 0.732, Recall 0.875, **F1 0.797**
- **Selection metric:** F1-score (balances false approvals vs. false rejections)
- **Key engineered features:** Total Income, EMI, Balance Income, Debt-to-Income Ratio, Risk Category
- **Two-layer decision:** ML creditworthiness + rule-based affordability sizing
- **Output:** Approved / Partially Approved / Rejected, amount in rupees (₹), plain-language reason
- **Deployment artifacts:** `best_model.pkl`, `preprocessor.pkl`, `impute_values.json`, `model_metadata.json`
- **Business outcome:** Automates initial risk screening, standardizes risk categorization, and feeds a live Power BI portfolio dashboard
