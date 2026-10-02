# Savexa — AI-Powered First Aid Assistant

Real-time injury detection and first-aid guidance system.

## Project Structure

```
Savexa/
├── backend/          Django REST API + AI model inference
├── cv/aidsense/      Dataset, trained model, CV scripts
└── frontend/         HTML/CSS/JS web interface
```

## How to Run

1. Open a terminal in the project root.
2. Activate the project environment: `.venv\Scripts\Activate.ps1`
3. Start Django: `python backend\manage.py runserver`
4. Serve `frontend/` over HTTP, for example: `python -m http.server 5500 --directory frontend`
5. Open `http://127.0.0.1:5500/index.html`.

Install the pinned environment with `python -m pip install -r requirements.txt`.

## AI Model

- File: `cv/aidsense/models/aidSense_multiclass.h5`
- Architecture: MobileNetV2
- Classes: **Burn**, **Cut**, **Abrasions**, **Bruises**, **Laceration**, **Stab_wound**, **Animal_bite**
- Input: RGB `224x224`, normalized to `0-1`
- The original two-class model remains at `cv/aidsense/models/aidSense_model.h5` as a protected backup.
- Invalid-image rejection has not been calibrated because a negative-image dataset is not yet available.

## Dataset Structure

```
cv/aidsense/dataset_clean/
├── train/
│   └── seven injury class folders
├── validation/
│   └── seven injury class folders
└── test/
    └── seven injury class folders
```

## Important Notes

- DO NOT delete db.sqlite3 (contains first-aid guidance)
- DO NOT rename or move either model without updating Django and evaluation paths
- DO NOT add injury classes without retraining the model
- Run Django with the project `.venv` so TensorFlow is available
