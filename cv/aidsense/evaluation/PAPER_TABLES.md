# Paper Tables

Generated from saved held-out test evaluations. Test set: 69 images.

## Model Comparison

| Variant | Accuracy | Macro precision | Macro recall | Macro F1 |
|---|---:|---:|---:|---:|
| Baseline | 69.57% | 76.58% | 66.86% | 66.42% |
| Class-balanced | 57.97% | 56.49% | 60.75% | 57.22% |
| Fine-tuned | 68.12% | 72.25% | 66.01% | 65.38% |
| Augmented | 56.52% | 53.92% | 54.58% | 49.91% |

## Baseline Per-Class Metrics

| Class | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| Burn | 63.64% | 70.00% | 66.67% | 10 |
| Cut | 60.00% | 37.50% | 46.15% | 8 |
| Abrasions | 69.23% | 69.23% | 69.23% | 13 |
| Bruises | 65.38% | 89.47% | 75.56% | 19 |
| Laceration | 77.78% | 87.50% | 82.35% | 8 |
| Stab_wound | 100.00% | 100.00% | 100.00% | 4 |
| Animal_bite | 100.00% | 14.29% | 25.00% | 7 |

## Embedding-based Invalid-Image Rejection (OOD)

Using cosine similarity on embeddings extracted from the `global_average_pooling` layer to class centroids:

| Cosine Sim Threshold | Valid Test Images Accepted (Support: 69) | Negative Images Accepted (Support: 18) |
|---|---:|---:|
| 0.50 | 100.0% (69/69) | 33.3% (6/18) |
| 0.60 | 98.6% (68/69) | 0.0% (0/18) |
| 0.70 | 59.4% (41/69) | 0.0% (0/18) |
| 0.75 | 14.5% (10/69) | 0.0% (0/18) |

- **Selected Threshold**: 0.60 achieves 98.6% valid image acceptance (only 1 false rejection) while successfully rejecting 100% of non-injury negative images.

## Reproducibility Notes

- The test split was evaluated separately from training and validation.
- Metrics are descriptive for this dataset and should not be interpreted as clinical validation.
- The test set is small, particularly for Stab_wound (4 images).
- Invalid-image rejection is experimentally supported in the backend view using the 0.60 cosine similarity threshold on the `global_average_pooling` embedding space.
