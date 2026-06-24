# GDSS2026_web

Django data manager for GDSS2026 — add training data, import CSVs, and export CSV files.

## Deploy on Render (recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/letuscode293/GDSS2026_web)

### One-click deploy

1. Push this repo to GitHub (`richard` branch).
2. Go to [Render Dashboard](https://dashboard.render.com/) → **New** → **Blueprint**.
3. Connect `https://github.com/letuscode293/GDSS2026_web`.
4. Render reads `render.yaml` and creates:
   - **Web service** — Django app
   - **PostgreSQL** — persistent database
5. Click **Apply** and wait for the build (~3–5 min).

Your app will be live at `https://gdss2026-web.onrender.com` (or similar).

### Manual deploy (alternative)

Create a **Web Service** on Render:

| Setting | Value |
|---------|--------|
| **Root directory** | *(leave blank — repo root)* |
| **Build command** | `./build.sh` |
| **Start command** | `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT` |
| **Python version** | `3.11.9` |

**Environment variables:**

| Key | Value |
|-----|--------|
| `DJANGO_SECRET_KEY` | Generate a random secret |
| `DEBUG` | `false` |
| `AUTO_PIPELINE` | `false` |
| `DATABASE_URL` | From a Render PostgreSQL instance |

Attach a **PostgreSQL** database and link `DATABASE_URL` to the web service.

### After deploy

- Open your Render URL and use the data manager.
- Upload CSVs or add records manually.
- Download exports from the home page.

> **Note:** Full auto-retrain (export → train → API reload) only works in the full monorepo with FastAPI running. On Render, `AUTO_PIPELINE=false` by default.

---

## Local development

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_datasets
python manage.py runserver 8001
```

Open http://127.0.0.1:8001/

## Monorepo automation (optional)

When running inside the full GDSS2026 project with `AUTO_PIPELINE=true`:

1. Export to `datasets/*.csv`
2. Run `scripts/train_tabular.py`
3. Reload FastAPI via `POST /reload-models`
