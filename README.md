# GDSS2026 Data Entry

Django web app for adding and importing crop and fertilizer training data.

**This is part 1 of GDSS2026.** Model training and deployment live in `ml_pipeline/` (separate repo).

## What this app does

- Add crop and fertilizer records via forms
- Bulk CSV upload
- Export data to CSV
- Trigger model retraining via **GitHub Actions** (`GITHUB_RETRAIN=true`)

## Does NOT do (by design)

- Train models locally on Render
- Serve predictions (that's `ml_pipeline/api/`)

## Deploy on Render

See `render.yaml`. Environment:

```env
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=...
DEBUG=false
GITHUB_RETRAIN=true
GITHUB_TOKEN=ghp_...
GITHUB_REPOSITORY=letuscode293/GDSS2026_web
```

## Local development

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_datasets
python manage.py runserver 8001
```

## GitHub Actions

`retrain-from-database.yml` exports this app's database → trains models in `ml_pipeline` repo → commits updated `.pkl` files.

Secrets: `GH_PAT`, `DATABASE_URL`, `DJANGO_SECRET_KEY`

## Local full pipeline (with sibling ml_pipeline/)

```bash
export AUTO_PIPELINE=true
# add data in browser → exports CSV, trains ml_pipeline, reloads API
```

Or from monorepo root:

```bash
cd ../ml_pipeline && python scripts/automate_pipeline.py
```
