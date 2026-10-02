"""Measure how often unrelated images are accepted by the injury classifier."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


CLASS_NAMES = ["Burn", "Cut", "Abrasions", "Bruises", "Laceration", "Stab_wound", "Animal_bite"]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative-dir", type=Path, required=True)
    parser.add_argument("--model", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_multiclass.h5")
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.50, 0.60, 0.70, 0.75, 0.80, 0.90])
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "rejection_results.json")
    args = parser.parse_args()

    image_paths = sorted(path for path in args.negative_dir.rglob("*") if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS)
    if not image_paths:
        raise FileNotFoundError(f"No images found in {args.negative_dir}")

    model = tf.keras.models.load_model(args.model)
    inputs = []
    for path in image_paths:
        image = Image.open(path).convert("RGB").resize((224, 224))
        inputs.append(np.asarray(image, dtype=np.float32) / 255.0)
    probabilities = model.predict(np.asarray(inputs), verbose=0)
    predictions = np.argmax(probabilities, axis=1)
    maximums = np.max(probabilities, axis=1)

    results = {
        "model": str(args.model.resolve()),
        "negative_directory": str(args.negative_dir.resolve()),
        "negative_images": len(image_paths),
        "class_names": CLASS_NAMES,
        "mean_maximum_probability": float(np.mean(maximums)),
        "maximum_probability": float(np.max(maximums)),
        "accepted_counts_by_threshold": {
            str(threshold): int(np.sum(maximums >= threshold)) for threshold in args.thresholds
        },
        "predicted_class_counts": {
            name: int(np.sum(predictions == index)) for index, name in enumerate(CLASS_NAMES)
        },
        "images": [
            {
                "file": str(path),
                "predicted_class": CLASS_NAMES[int(prediction)],
                "maximum_probability": float(maximum),
            }
            for path, prediction, maximum in zip(image_paths, predictions, maximums)
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    csv_path = args.output.with_name(f"{args.output.stem}.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["file", "predicted_class", "maximum_probability"])
        writer.writeheader()
        writer.writerows(results["images"])
    print(json.dumps({key: results[key] for key in ("negative_images", "mean_maximum_probability", "maximum_probability", "accepted_counts_by_threshold")}, indent=2))
    print(f"Saved results: {args.output}")
    print(f"Saved predictions: {csv_path}")


if __name__ == "__main__":
    main()