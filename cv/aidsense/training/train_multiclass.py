"""Train a seven-class model from the existing MobileNetV2 feature extractor."""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import tensorflow as tf


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


def load_split(path: Path, batch_size: int, shuffle: bool, augment: bool = False) -> tf.data.Dataset:
    dataset = tf.keras.utils.image_dataset_from_directory(
        path,
        labels="inferred",
        class_names=CLASS_NAMES,
        label_mode="int",
        image_size=IMAGE_SIZE,
        batch_size=batch_size,
        shuffle=shuffle,
        seed=2026,
    )
    if augment:
        augmenter = tf.keras.Sequential([
            tf.keras.layers.RandomFlip('horizontal'),
            tf.keras.layers.RandomRotation(0.08),
            tf.keras.layers.RandomZoom(0.1),
        ], name='training_augmentation')
        dataset = dataset.map(lambda images, labels: (augmenter(tf.cast(images, tf.float32) / 255.0, training=True), labels))
    else:
        dataset = dataset.map(lambda images, labels: (tf.cast(images, tf.float32) / 255.0, labels))
    return dataset


def image_count(path: Path) -> int:
    return sum(1 for item in path.rglob("*") if item.is_file() and item.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"})


def class_weights(path: Path) -> dict[int, float]:
    counts = [image_count(path / class_name) for class_name in CLASS_NAMES]
    total = sum(counts)
    return {index: total / (len(CLASS_NAMES) * count) for index, count in enumerate(counts) if count}


def build_model(old_model_path: Path) -> tf.keras.Model:
    old_model = tf.keras.models.load_model(old_model_path)
    feature_extractor = next(
        (layer for layer in old_model.layers if isinstance(layer, tf.keras.Model)), None
    )
    if feature_extractor is None:
        raise RuntimeError("Could not find the existing MobileNetV2 feature extractor")

    feature_extractor.trainable = False
    inputs = tf.keras.Input(shape=(*IMAGE_SIZE, 3), name="image")
    features = feature_extractor(inputs, training=False)
    features = tf.keras.layers.GlobalAveragePooling2D(name="global_average_pooling")(features)
    features = tf.keras.layers.Dense(128, activation="relu", name="classifier_dense")(features)
    features = tf.keras.layers.Dropout(0.4, name="classifier_dropout")(features)
    outputs = tf.keras.layers.Dense(len(CLASS_NAMES), activation="softmax", name="injury_output")(features)
    return tf.keras.Model(inputs, outputs, name="aidSense_multiclass")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).parents[1] / "dataset_clean")
    parser.add_argument("--old-model", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_model.h5")
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_multiclass.h5")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.0001)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite existing model: {args.output}")

    train_data = load_split(args.dataset / "train", args.batch_size, shuffle=True, augment=True)
    validation_data = load_split(args.dataset / "validation", args.batch_size, shuffle=False)
    weights = class_weights(args.dataset / "train")
    model = build_model(args.old_model)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    history = model.fit(
        train_data,
        validation_data=validation_data,
        epochs=args.epochs,
        class_weight=weights,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=4, restore_best_weights=True
            )
        ],
    )
    training_seconds = time.perf_counter() - started
    model.save(args.output)

    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "tensorflow": tf.__version__,
        "dataset": str(args.dataset.resolve()),
        "class_names": CLASS_NAMES,
        "input_shape": [224, 224, 3],
        "train_images": image_count(args.dataset / "train"),
        "validation_images": image_count(args.dataset / "validation"),
        "epochs_requested": args.epochs,
        "epochs_completed": len(history.history["loss"]),
        "batch_size": args.batch_size,
        "optimizer": "Adam",
        "learning_rate": args.learning_rate,
        "loss": "SparseCategoricalCrossentropy",
        "architecture": "Existing MobileNetV2 feature extractor + GAP + Dense(128) + Dropout(0.4) + Dense(7, softmax)",
        "feature_extractor_frozen": True,
        "augmentation": ["RandomFlip(horizontal)", "RandomRotation(0.08)", "RandomZoom(0.1)"],
        "class_weights": {CLASS_NAMES[index]: weight for index, weight in weights.items()},
        "training_seconds": training_seconds,
        "history": {key: [float(value) for value in values] for key, values in history.history.items()},
    }
    metadata_path = args.output.with_suffix(".training.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved model: {args.output}")
    print(f"Saved metadata: {metadata_path}")


if __name__ == "__main__":
    main()