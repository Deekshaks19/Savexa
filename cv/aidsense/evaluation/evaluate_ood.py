"""Evaluate Out-of-Distribution (OOD) detection using model embeddings and cosine similarity."""

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


def get_embeddings(model: tf.keras.Model, image_paths: list[Path]) -> np.ndarray:
    """Extract global_average_pooling embeddings for a list of image paths."""
    embedding_model = tf.keras.Model(inputs=model.input, outputs=model.get_layer("global_average_pooling").output)
    inputs = []
    for path in image_paths:
        image = Image.open(path).convert("RGB").resize((224, 224))
        inputs.append(np.asarray(image, dtype=np.float32) / 255.0)
    
    # Process in batches to avoid OOM
    embeddings = []
    batch_size = 32
    for i in range(0, len(inputs), batch_size):
        batch = np.asarray(inputs[i:i+batch_size])
        batch_embeddings = embedding_model.predict(batch, verbose=0)
        embeddings.append(batch_embeddings)
    return np.concatenate(embeddings, axis=0)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between two sets of vectors."""
    # a: (N, D), b: (M, D) or (D,)
    norm_a = np.linalg.norm(a, axis=-1, keepdims=True)
    if b.ndim == 1:
        norm_b = np.linalg.norm(b)
        return np.dot(a, b) / (norm_a.squeeze(-1) * norm_b + 1e-8)
    else:
        norm_b = np.linalg.norm(b, axis=-1, keepdims=True)
        return np.dot(a, b.T) / (np.dot(norm_a, norm_b.T) + 1e-8)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).parents[1] / "dataset_clean")
    parser.add_argument("--negative-dir", type=Path, default=Path(__file__).parents[0] / "negative_images")
    parser.add_argument("--model", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_multiclass.h5")
    parser.add_argument("--thresholds", type=float, nargs="+", default=[0.50, 0.60, 0.70, 0.75, 0.80, 0.85, 0.90])
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "ood_results.json")
    args = parser.parse_args()

    # Load model
    model = tf.keras.models.load_model(args.model)

    # 1. Compute Centroids from training data
    print("Computing class centroids from train split...")
    train_paths_by_class = {}
    train_embeddings_by_class = {}
    class_centroids = {}

    for label_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = args.dataset / "train" / class_name
        paths = sorted(p for p in class_dir.glob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
        train_paths_by_class[class_name] = paths
        if paths:
            embeddings = get_embeddings(model, paths)
            train_embeddings_by_class[class_name] = embeddings
            class_centroids[class_name] = np.mean(embeddings, axis=0)
            print(f"  {class_name}: processed {len(paths)} train images.")
        else:
            print(f"  Warning: No train images for class {class_name}")

    # Convert centroids to numpy array for fast computation
    centroids_arr = np.array([class_centroids[name] for name in CLASS_NAMES]) # (7, 128)

    # 2. Evaluate on held-out test data (Valid injuries)
    print("\nEvaluating on test split...")
    test_paths = []
    test_true_labels = []
    for label_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = args.dataset / "test" / class_name
        paths = sorted(p for p in class_dir.glob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
        test_paths.extend(paths)
        test_true_labels.extend([label_idx] * len(paths))

    test_embeddings = get_embeddings(model, test_paths)
    # Predict using model outputs to simulate deployment
    test_inputs = []
    for p in test_paths:
        image = Image.open(p).convert("RGB").resize((224, 224))
        test_inputs.append(np.asarray(image, dtype=np.float32) / 255.0)
    test_preds = model.predict(np.asarray(test_inputs), verbose=0)
    test_pred_labels = np.argmax(test_preds, axis=1)

    # Compute similarity to predicted class centroid for each test image
    test_similarities = []
    for idx, (emb, pred_label) in enumerate(zip(test_embeddings, test_pred_labels)):
        centroid = class_centroids[CLASS_NAMES[pred_label]]
        sim = cosine_similarity(emb[np.newaxis, :], centroid)[0]
        test_similarities.append(float(sim))
    test_similarities = np.array(test_similarities)

    # 3. Evaluate on negative images
    print("Evaluating on negative images...")
    negative_paths = sorted(p for p in args.negative_dir.glob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS)
    if not negative_paths:
        print("No negative images found!")
        return

    neg_embeddings = get_embeddings(model, negative_paths)
    neg_inputs = []
    for p in negative_paths:
        image = Image.open(p).convert("RGB").resize((224, 224))
        neg_inputs.append(np.asarray(image, dtype=np.float32) / 255.0)
    neg_preds = model.predict(np.asarray(neg_inputs), verbose=0)
    neg_pred_labels = np.argmax(neg_preds, axis=1)

    neg_similarities = []
    for idx, (emb, pred_label) in enumerate(zip(neg_embeddings, neg_pred_labels)):
        centroid = class_centroids[CLASS_NAMES[pred_label]]
        sim = cosine_similarity(emb[np.newaxis, :], centroid)[0]
        neg_similarities.append(float(sim))
    neg_similarities = np.array(neg_similarities)

    # Summary of similarities
    print("\nSimilarity Stats:")
    print(f"  Valid Test Images Similarity: mean={np.mean(test_similarities):.4f}, min={np.min(test_similarities):.4f}, max={np.max(test_similarities):.4f}")
    print(f"  Negative Images Similarity:   mean={np.mean(neg_similarities):.4f}, min={np.min(neg_similarities):.4f}, max={np.max(neg_similarities):.4f}")

    # Threshold analysis
    accepted_test_by_threshold = {}
    accepted_neg_by_threshold = {}
    for threshold in args.thresholds:
        accepted_test = np.sum(test_similarities >= threshold)
        accepted_neg = np.sum(neg_similarities >= threshold)
        accepted_test_by_threshold[str(threshold)] = {
            "accepted": int(accepted_test),
            "pct": float(accepted_test / len(test_similarities) * 100)
        }
        accepted_neg_by_threshold[str(threshold)] = {
            "accepted": int(accepted_neg),
            "pct": float(accepted_neg / len(neg_similarities) * 100)
        }
        print(f"  At threshold {threshold:.2f}:")
        print(f"    Valid images accepted:    {accepted_test}/{len(test_similarities)} ({accepted_test/len(test_similarities)*100:.1f}%)")
        print(f"    Negative images accepted: {accepted_neg}/{len(neg_similarities)} ({accepted_neg/len(neg_similarities)*100:.1f}%)")

    # Save results
    results = {
        "model": str(args.model.resolve()),
        "test_images": len(test_paths),
        "negative_images": len(negative_paths),
        "mean_test_similarity": float(np.mean(test_similarities)),
        "min_test_similarity": float(np.min(test_similarities)),
        "mean_neg_similarity": float(np.mean(neg_similarities)),
        "max_neg_similarity": float(np.max(neg_similarities)),
        "thresholds_analysis": {
            str(t): {
                "threshold": t,
                "valid_accepted": accepted_test_by_threshold[str(t)]["accepted"],
                "valid_accepted_pct": accepted_test_by_threshold[str(t)]["pct"],
                "negative_accepted": accepted_neg_by_threshold[str(t)]["accepted"],
                "negative_accepted_pct": accepted_neg_by_threshold[str(t)]["pct"],
            } for t in args.thresholds
        },
        "centroids": {name: centroid.tolist() for name, centroid in class_centroids.items()}
    }

    args.output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved OOD evaluation results to: {args.output}")


if __name__ == "__main__":
    main()
