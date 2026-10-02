"""Create a duplicate-free, deterministic dataset split without changing the source dataset."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from collections import defaultdict
from pathlib import Path
from random import Random


CLASSES = [
    "Abrasions",
    "Animal_bite",
    "Bruises",
    "Burn",
    "Cut",
    "Laceration",
    "Stab_wound",
]
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp"}
SPLIT_RATIOS = {"train": 0.70, "validation": 0.15, "test": 0.15}


def image_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for chunk in iter(lambda: image_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_unique_images(source: Path) -> dict[str, dict[str, list[Path]]]:
    images: dict[str, dict[str, list[Path]]] = defaultdict(lambda: defaultdict(list))
    for path in sorted(source.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        relative_parts = path.relative_to(source).parts
        if len(relative_parts) < 2:
            continue
        injury_class = relative_parts[1]
        if injury_class in CLASSES:
            images[injury_class][image_hash(path)].append(path)
    return images


def split_count(total: int) -> dict[str, int]:
    train_count = round(total * SPLIT_RATIOS["train"])
    validation_count = round(total * SPLIT_RATIOS["validation"])
    return {
        "train": train_count,
        "validation": validation_count,
        "test": total - train_count - validation_count,
    }


def prepare_dataset(source: Path, destination: Path, seed: int) -> dict:
    unique_images = collect_unique_images(source)
    if destination.exists():
        raise FileExistsError(f"Destination already exists: {destination}")

    report = {"seed": seed, "source": str(source), "destination": str(destination), "classes": {}}
    for injury_class in CLASSES:
        hashes = sorted(unique_images.get(injury_class, {}))
        Random(seed + CLASSES.index(injury_class)).shuffle(hashes)
        counts = split_count(len(hashes))
        class_report = {"unique": len(hashes), **counts, "source_files": []}
        start = 0
        for split in ("train", "validation", "test"):
            split_hashes = hashes[start : start + counts[split]]
            start += counts[split]
            output_dir = destination / split / injury_class
            output_dir.mkdir(parents=True, exist_ok=True)
            for digest in split_hashes:
                source_path = sorted(unique_images[injury_class][digest])[0]
                output_name = f"{digest[:16]}{source_path.suffix.lower()}"
                shutil.copy2(source_path, output_dir / output_name)
                class_report["source_files"].append(
                    {"split": split, "source": str(source_path), "sha256": digest}
                )
        report["classes"][injury_class] = class_report

    destination.mkdir(parents=True, exist_ok=True)
    (destination / "dataset_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[1] / "dataset")
    parser.add_argument("--destination", type=Path, default=Path(__file__).parents[1] / "dataset_clean")
    parser.add_argument("--seed", type=int, default=2026)
    args = parser.parse_args()

    report = prepare_dataset(args.source.resolve(), args.destination.resolve(), args.seed)
    print("Class | Unique | Train | Validation | Test")
    for injury_class in CLASSES:
        values = report["classes"][injury_class]
        print(
            f"{injury_class} | {values['unique']} | {values['train']} | "
            f"{values['validation']} | {values['test']}"
        )
    print(f"Created: {args.destination.resolve()}")


if __name__ == "__main__":
    main()