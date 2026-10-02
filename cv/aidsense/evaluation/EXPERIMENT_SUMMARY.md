# AidSense Experiment Summary

This summary records measured results from the current Savexa experiments. It is not a claim of clinical performance.

## Dataset

The original dataset contained duplicate copies across its train, validation, and test folders. A separate `dataset_clean` copy was created without changing the original files.

| Class | Unique images | Train | Validation | Test |
|---|---:|---:|---:|---:|
| Abrasions | 85 | 59 | 13 | 13 |
| Animal_bite | 50 | 35 | 8 | 7 |
| Bruises | 122 | 85 | 18 | 19 |
| Burn | 62 | 43 | 9 | 10 |
| Cut | 52 | 36 | 8 | 8 |
| Laceration | 52 | 36 | 8 | 8 |
| Stab_wound | 23 | 16 | 3 | 4 |
| **Total** | **446** | **310** | **67** | **69** |

The clean split contains no exact hash duplicates across train, validation, and test. Pillow reported no unreadable image files in the source dataset.

## Model and Training

- Architecture: existing MobileNetV2 feature extractor, GlobalAveragePooling2D, Dense(128, ReLU), Dropout(0.4), Dense(7, softmax)
- Input: RGB `224x224`, values normalized to `0-1`
- Classes: Burn, Cut, Abrasions, Bruises, Laceration, Stab_wound, Animal_bite
- Optimizer: Adam
- Learning rate: `0.0001`
- Loss: SparseCategoricalCrossentropy
- Batch size: `16`
- Requested epochs: `15`
- Backbone: frozen for the baseline model
- Baseline training time: `84.16` seconds

## Held-Out Test Results

The baseline result below was produced using only the 69-image clean test split.

| Metric | Result |
|---|---:|
| Accuracy | 69.57% |
| Macro precision | 76.58% |
| Macro recall | 66.86% |
| Macro F1 | 66.42% |

Per-class results and the confusion matrix are stored in `evaluation_results.json` and `evaluation_results_confusion_matrix.csv`.

## Comparison Experiments

| Variant | Accuracy | Macro F1 |
|---|---:|---:|
| Baseline | 69.57% | 66.42% |
| Class-balanced training | 57.97% | 57.22% |
| Fine-tuned final backbone layers | 68.12% | 65.38% |

The baseline remains the selected Django model. Neither comparison variant should replace it without further data and validation.

## Limitations and Pending Experiment

- The test set contains only 69 images.
- `Stab_wound` has only 23 unique images and 4 test images.
- `Animal_bite` recall was 14.3% in the baseline test report.
- Invalid-image rejection is experimentally supported using cosine similarity on embeddings, but is not claimed to be perfect.
- Body-region detection is not implemented.

### Embedding-Based OOD Rejection Experiment

We extracted image embeddings from the model's `global_average_pooling` layer (1280 dimensions) and computed the cosine similarity to the centroids of training classes. 

- **Valid Test Images Similarity**: mean = 0.7042, min = 0.5913, max = 0.7987
- **Negative Images Similarity**: mean = 0.4822, min = 0.3923, max = 0.5831

By setting a cosine similarity threshold of **0.60**, we achieve:
- **Valid injury images accepted**: 68 / 69 (98.6%)
- **Negative images accepted (OOD)**: 0 / 18 (0.0%)

This embedding-based OOD approach provides a reliable threshold for invalid-image rejection and is now active in the Django API endpoint (`POST /api/detect/`) returning `'valid': False` when cosine similarity is below 0.60.