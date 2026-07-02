# Loan Approval Prediction System — Simple Interview Guide

This is the easy version. Short sentences, simple words, no jargon
without an explanation. Read this if you want to explain the project
confidently without needing deep ML/SQL background.

---

## 1. What is this project? (Say this first)

"I built a system that looks at a person's details — income, credit
score, job status, how much loan they want — and decides two things:

1. Should this loan be **approved or rejected**?
2. If approved, **how much money** should actually be given?
3. If rejected, **why** — in plain words.

I used Python to clean the data and build the prediction model, SQL to
store and search the data, and Power BI to show charts and reports."

That's it. That's the whole project in one breath.

---

## 2. How does it work? (Simple steps)

Think of it like an assembly line. Each step takes the data from the
step before and improves it.

1. **Get the data** — a list of loan applicants (income, credit score, etc.)
2. **Clean the data** — fix missing values, fix typos, remove duplicate entries
3. **Store it in SQL** — like putting it into an organized filing cabinet you can search
4. **Create new useful info (features)** — like calculating monthly EMI, or how much money is left after paying EMI
5. **Train the model** — show the computer thousands of past examples so it learns the pattern of who gets approved
6. **Test the model** — check how good its guesses are
7. **Pick the best model** — out of 3 models tried, keep the one that guessed best
8. **Save the model** — so we can reuse it without retraining every time
9. **Predict new applicants** — feed a new person's details in, get a decision
10. **Send data to Power BI** — so managers can see charts, not just numbers

---

## 3. What does each folder do? (Very simple)

| Folder | What's inside, in plain words |
|---|---|
| `data/` | All the spreadsheets — raw data, cleaned data, final data for Power BI |
| `database/` | The SQL files — how the data is organized and searched |
| `src/` | All the Python code — one file per job (cleaning, feature-making, training, predicting) |
| `models/` | The trained "brain" saved to disk, so we don't have to retrain it every time |
| `outputs/` | Results — score reports, charts, prediction results |
| `scripts/` | One button (`run_pipeline.py`) that runs everything from start to finish |

If asked "what's in src?", just say: "Each file does one job — one cleans
the data, one creates new useful columns, one trains the models, one
makes the final decision, one is used to predict new applicants."

---

## 4. What is "Machine Learning" doing here? (No jargon)

Imagine you show a child 1,000 old loan applications, and for each one
you say "this got approved" or "this got rejected." After seeing enough
examples, the child starts noticing patterns — like "people with bad
credit history usually get rejected."

That's what the model does. It looks at thousands of past examples and
learns the pattern. Then, when a new person applies, it uses that
pattern to guess: approve or reject.

---

## 5. The 3 models I compared (Simple explanation)

I didn't just use one method — I tried three and picked the best one.

1. **Logistic Regression** — the simplest one. It looks at each factor
   (income, credit score, etc.) and gives it a weight, then adds
   everything up to decide. Easy to explain to anyone.
2. **Decision Tree** — works like a flowchart of yes/no questions.
   "Is credit history good? → Yes → Is income above X? → Yes → Approve."
3. **Random Forest** — instead of one flowchart, it builds many
   flowcharts and lets them vote. Usually more accurate, but harder to
   explain.

**Result:** Logistic Regression actually won in my project. Simple
doesn't always mean worse.

---

## 6. How do you know if the model is "good"? (Simple explanation)

Imagine the model makes 100 guesses. We check:

- **Accuracy** — out of 100 guesses, how many were correct overall?
- **Precision** — out of everyone the model said "approve," how many
  really deserved approval? (Are we being too generous?)
- **Recall** — out of everyone who really deserved approval, how many did
  the model correctly approve? (Are we rejecting good people by mistake?)
- **F1-score** — one single number that balances Precision and Recall
  together, so you don't only look at one and ignore the other.

I picked the model with the best F1-score, because in loans, both kinds
of mistakes are costly — approving a risky person, and rejecting a good
one.

---

## 7. How do we decide the loan amount and the reason? (Simple explanation)

The model only says "approve" or "reject." But that's not enough for a
real bank. So I added a second, simple rule-based step:

- I calculate how much EMI the person can actually afford, based on their
  income.
- If they asked for more than they can afford, we approve a **smaller
  amount** instead of the full amount.
- If we reject someone, the system lists the actual reasons — like "low
  credit score," "too much existing debt," "unemployed," etc. — instead
  of just saying "no."

This makes it feel like a real bank decision, not just a yes/no answer.

---

## 8. Simple sample interview questions and answers

**Q: What does your project do?**
> A: "It predicts whether a loan should be approved or rejected, and if
> approved, how much amount should be given, using a person's income,
> credit score, and other details."

**Q: What tools did you use?**
> A: "Python for cleaning data and building the model, SQL for storing
> and organizing data, and Power BI for showing dashboards and charts."

**Q: What is a machine learning model, in simple words?**
> A: "It's a program that learns patterns from past examples, and uses
> those patterns to make predictions on new data."

**Q: Which models did you try, and which one did you pick?**
> A: "I tried Logistic Regression, Decision Tree, and Random Forest.
> Logistic Regression gave the best results, so I picked that one."

**Q: How did you clean the data?**
> A: "I filled in missing values — using the most common value for
> categories, and the middle value (median) for numbers. I also removed
> duplicate records and fixed inconsistent text like extra spaces or
> mixed uppercase/lowercase."

**Q: What new features (columns) did you create?**
> A: "Total income, monthly EMI, how much income is left after EMI,
> debt-to-income ratio, and a simple risk category — Low, Medium, or
> High risk."

**Q: How do you check if the model is accurate?**
> A: "I check accuracy, precision, recall, and F1-score, and also look at
> a confusion matrix, which shows how many predictions were right or
> wrong for each class."

**Q: Why not just use accuracy alone?**
> A: "Because accuracy can be misleading — a model can look accurate
> overall but still be bad at spotting one important group, like risky
> applicants. So I also check precision and recall, and use F1-score to
> balance both."

**Q: How does the system decide the loan amount, not just approve/reject?**
> A: "After the model says 'approve,' I calculate the maximum amount the
> person can afford to repay based on their income. If they asked for
> more than that, I approve a smaller amount instead of the full one."

**Q: What happens when someone is rejected?**
> A: "The system checks the reasons — like low credit score, high debt,
> unemployment, or too many existing loans — and shows those reasons in
> plain language instead of just saying 'rejected.'"

**Q: Why did you use SQL if you already have the data in Python?**
> A: "SQL is how real companies store and search large amounts of data.
> It lets people who don't know Python — like analysts or managers — run
> queries and reports directly on the data."

**Q: What is Power BI used for here?**
> A: "It's used to build dashboards — charts showing approval rate,
> rejection rate, risk categories, income trends, and loan amount trends
> — so business people can understand the results without looking at
> code."

**Q: What would you improve if you had more time?**
> A: "I'd use real loan data instead of generated sample data, try to
> fine-tune the models further, and add a way to track if the model's
> accuracy drops over time."

---

## 9. If you get stuck, use this one-line safety answer

"This project takes an applicant's financial details, cleans and
organizes the data, trains a few machine learning models to predict loan
approval, picks the best one, and then adds a simple business rule on
top to decide the exact approved amount or the reason for rejection —
with everything also feeding into a Power BI dashboard for reporting."

Memorize just this one paragraph if nothing else. It covers the whole
project.
