# GDSS2026_web

Django data manager for GDSS2026 — add training data, import CSVs, and trigger the automated retrain pipeline.

## Quick start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_datasets
python manage.py runserver 8001
```

Open http://127.0.0.1:8001/

## Automated pipeline

On data changes (when `AUTO_PIPELINE=true`):

1. Export to `datasets/*.csv`
2. Run `scripts/train_tabular.py`
3. Reload FastAPI via `POST /reload-models`

## Features

- Add crop and fertilizer records via forms
- Bulk CSV upload
- View and download data
- Run full pipeline from the home page
