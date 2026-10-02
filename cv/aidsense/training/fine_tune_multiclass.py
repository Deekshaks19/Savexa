"""Fine-tune the last MobileNetV2 layers starting from the current multiclass model."""

from __future__ import annotations

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import tensorflow as tf

from train_multiclass import CLASS_NAMES, IMAGE_SIZE, image_count, load_split


def prepare_model(model_path: Path, layers_to_unfreeze: int) -> tf.keras.Model:
    model = tf.keras.models.load_model(model_path)
    feature_extractor = next(
        (layer for layer in model.layers if isinstance(layer, tf.keras.Model)), None
    )
    if feature_extractor is None:
        raise RuntimeError("Could not find the MobileNetV2 feature extractor")

    feature_extractor.trainable = True
    first_trainable = max(0, len(feature_extractor.layers) - layers_to_unfreeze)
    for index, layer in enumerate(feature_extractor.layers):
        layer.trainable = index >= first_trainable and not isinstance(layer, tf.keras.layers.BatchNormalization)
    return model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=Path, default=Path(__file__).parents[1] / "dataset_clean")
    parser.add_argument("--model", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_multiclass.h5")
    parser.add_argument("--output", type=Path, default=Path(__file__).parents[1] / "models" / "aidSense_multiclass_finetuned.h5")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--learning-rate", type=float, default=0.00001)
    parser.add_argument("--layers-to-unfreeze", type=int, default=20)
    args = parser.parse_args()

    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite existing model: {args.output}")

    train_data = load_split(args.dataset / "train", args.batch_size, shuffle=True)
    validation_data = load_split(args.dataset / "validation", args.batch_size, shuffle=False)
    model = prepare_model(args.model, args.layers_to_unfreeze)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=args.learning_rate),
        loss=tf.keras.losses.SparseCategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    started = time.perf_counter()
    history = model.fit(
        train_data,
        validation_data=validation_data,
        epochs=args.epochs,
        callbacks=[tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=2, restore_best_weights=True)],
    )
    training_seconds = time.perf_counter() - started
    args.output.parent.mkdir(parents=True, exist_ok=True)
    model.save(args.output)
    metadata = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(),
        "tensorflow": tf.__version__,
        "dataset": str(args.dataset.resolve()),
        "class_names": CLASS_NAMES,
        "input_shape": [*IMAGE_SIZE, 3],
        "train_images": image_count(args.dataset / "train"),
        "validation_images": image_count(args.dataset / "validation"),
        "epochs_requested": args.epochs,
        "epochs_completed": len(history.history["loss"]),
        "batch_size": args.batch_size,
        "optimizer": "Adam",
        "learning_rate": args.learning_rate,
        "loss": "SparseCategoricalCrossentropy",
        "layers_unfrozen": args.layers_to_unfreeze,
        "batch_normalization_layers_frozen": True,
        "training_seconds": training_seconds,
        "history": {key: [float(value) for value in values] for key, values in history.history.items()},
    }
    metadata_path = args.output.with_suffix(".training.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Saved model: {args.output}")
    print(f"Saved metadata: {metadata_path}")


if __name__ == "__main__":
    main()