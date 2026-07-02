"""
Reusable model evaluation utilities: metric computation, confusion matrix
plotting, and a formatted text report — shared by train_models.py.
"""

import os

import matplotlib
matplotlib.use("Agg")  # headless rendering, no display server required
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "precision": round(precision_score(y_true, y_pred, pos_label=1), 4),
        "recall": round(recall_score(y_true, y_pred, pos_label=1), 4),
        "f1_score": round(f1_score(y_true, y_pred, pos_label=1), 4),
    }


def plot_confusion_matrix(y_true, y_pred, model_name: str, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])

    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Rejected (0)", "Approved (1)"],
        yticklabels=["Rejected (0)", "Approved (1)"],
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"Confusion Matrix - {model_name}")
    fig.tight_layout()

    out_path = os.path.join(output_dir, f"confusion_matrix_{model_name.replace(' ', '_').lower()}.png")
    fig.savefig(out_path, dpi=120)
    plt.close(fig)
    return out_path


def build_text_report(results: dict, best_model_name: str) -> str:
    lines = [
        "=" * 70,
        "LOAN APPROVAL PREDICTION - MODEL EVALUATION REPORT",
        "=" * 70,
        "",
    ]
    for name, r in results.items():
        lines.append(f"Model: {name}")
        lines.append("-" * 40)
        lines.append(f"  Accuracy : {r['metrics']['accuracy']}")
        lines.append(f"  Precision: {r['metrics']['precision']}")
        lines.append(f"  Recall   : {r['metrics']['recall']}")
        lines.append(f"  F1-score : {r['metrics']['f1_score']}")
        lines.append("")
        lines.append("  Classification report:")
        lines.append(classification_report(r["y_true"], r["y_pred"], target_names=["Rejected", "Approved"]))
        lines.append("")

    lines.append("=" * 70)
    lines.append(f"BEST MODEL SELECTED: {best_model_name} (highest F1-score)")
    lines.append("=" * 70)
    return "\n".join(lines)
