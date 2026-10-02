"""Generate Markdown tables from saved evaluation results."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parent
EXPERIMENTS = [
    ("Baseline", "evaluation_results.json"),
    ("Class-balanced", "balanced_evaluation_results.json"),
    ("Fine-tuned", "finetuned_evaluation_results.json"),
    ("Augmented", "augmented_evaluation_results.json"),
]


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def main() -> None:
    results = [(name, json.loads((ROOT / filename).read_text(encoding="utf-8"))) for name, filename in EXPERIMENTS]
    lines = [
        "# Paper Tables",
        "",
        "Generated from saved held-out test evaluations. Test set: 69 images.",
        "",
        "## Model Comparison",
        "",
        "| Variant | Accuracy | Macro precision | Macro recall | Macro F1 |",
        "|---|---:|---:|---:|---:|",
    ]
    for name, result in results:
        lines.append(
            f"| {name} | {percent(result['accuracy'])} | {percent(result['macro_precision'])} | "
            f"{percent(result['macro_recall'])} | {percent(result['macro_f1'])} |"
        )

    baseline = results[0][1]
    lines.extend([
        "",
        "## Baseline Per-Class Metrics",
        "",
        "| Class | Precision | Recall | F1 | Support |",
        "|---|---:|---:|---:|---:|",
    ])
    for class_name in baseline["class_names"]:
        metrics = baseline["per_class"][class_name]
        lines.append(
            f"| {class_name} | {percent(metrics['precision'])} | {percent(metrics['recall'])} | "
            f"{percent(metrics['f1-score'])} | {int(metrics['support'])} |"
        )

    lines.extend([
        "",
        "## Reproducibility Notes",
        "",
        "- The test split was evaluated separately from training and validation.",
        "- Metrics are descriptive for this dataset and should not be interpreted as clinical validation.",
        "- The test set is small, particularly for Stab_wound (4 images).",
        "- Invalid-image rejection is not included because no acceptable threshold was found in the initial negative-image experiment.",
    ])
    output = ROOT / "PAPER_TABLES.md"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved: {output}")


if __name__ == "__main__":
    main()