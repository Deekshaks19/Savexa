"""Evaluate the trained model only on the clean, held-out test split."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, precision_score, recall_score


CLASS_NAMES = [
    "Burn",
    "Cut",
    "Abrasions",
    "Bruises",
    "Laceration",
    "Stab_wound",
    "Animal_bite",
]
IMAGE_SIZE = (224, 224)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def load_test_data(path: Path, batch_size: int) -> tf.data.Dataset:
    dataset = tf.keras.utils.image_dataset_from_directory(
        path,
        labels="inferred",
        class_names=CLASS_NAMES,
        label_mode="int",
        image_size=IMAGE_SIZE,
        batch_size=batch_size,
        shuffle=False,
    )
    return dataset.map(lambda images, labels: (tf.cast(images, tf.float32) / 255.0, labels))


def image_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file() and item.suffix.lower() in IMAGE_EXTENSIONS)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).parents[1] / "dataset_clean")
    parser.add_argument("--model", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_multiclass.h5")
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "evaluation_results.json")
    parser.add_argument("--batch-size", type=int, default=16)
    args = parser.parse_args()

    test_path = args.dataset / "test"
    model = tf.keras.models.load_model(args.model)
    test_data = load_test_data(test_path, args.batch_size)

    labels = np.concatenate([batch_labels.numpy() for _, batch_labels in test_data], axis=0)
    started = time.perf_counter()
    probabilities = model.predict(test_data, verbose=0)
    inference_seconds = time.perf_counter() - started
    predictions = np.argmax(probabilities, axis=1)

    matrix = confusion_matrix(labels, predictions, labels=range(len(CLASS_NAMES)))
    report = classification_report(
        labels,
        predictions,
        labels=range(len(CLASS_NAMES)),
        target_names=CLASS_NAMES,
        output_dict=True,
        zero_division=0,
    )
    results = {
        "model": str(args.model.resolve()),
        "test_dataset": str(test_path.resolve()),
        "test_images": int(len(labels)),
        "class_names": CLASS_NAMES,
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_precision": float(precision_score(labels, predictions, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(labels, predictions, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "per_class": {name: report[name] for name in CLASS_NAMES},
        "confusion_matrix": matrix.tolist(),
        "actual_counts": {name: int((labels == index).sum()) for index, name in enumerate(CLASS_NAMES)},
        "prediction_counts": {name: int((predictions == index).sum()) for index, name in enumerate(CLASS_NAMES)},
        "inference_seconds_total": inference_seconds,
        "inference_seconds_per_image": inference_seconds / len(labels),
        "batch_size": args.batch_size,
        "loss": "SparseCategoricalCrossentropy",
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    matrix_path = args.output.with_name(f"{args.output.stem}_confusion_matrix.csv")
    with matrix_path.open("w", newline="", encoding="utf-8") as matrix_file:
        writer = csv.writer(matrix_file)
        writer.writerow(["actual\\predicted", *CLASS_NAMES])
        writer.writerows([[CLASS_NAMES[index], *row] for index, row in enumerate(matrix)])
    print(json.dumps({key: results[key] for key in ("test_images", "accuracy", "macro_precision", "macro_recall", "macro_f1")}, indent=2))
    print(f"Saved results: {args.output}")
    print(f"Saved confusion matrix: {matrix_path}")


if __name__ == "__main__":
    main()