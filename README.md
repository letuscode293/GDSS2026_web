# GDSS2026_web

Django data manager for GDSS2026 — add training data, import CSVs, and trigger model retraining via GitHub Actions.

## GitHub Actions retrain pipeline

Workflow: `.github/workflows/retrain-from-database.yml`

**What it does:**
1. Connects to your Render PostgreSQL (`DATABASE_URL` secret)
2. Exports all records to CSV
3. Checks out the [tutorial](https://github.com/letuscode293/tutorial) repo
4. Runs `train_tabular.py` and tests
5. Commits updated `models/*.pkl` and `datasets/*.csv` to GitHub

**Triggers:**
| When | How |
|------|-----|
| Manual | GitHub → Actions → **Retrain from database** → Run workflow |
| Daily | Scheduled at 06:00 UTC |
| On data change | Set `GITHUB_RETRAIN=true` on Render (see below) |

### Required GitHub secrets

In **GDSS2026_web** repo → Settings → Secrets → Actions:

| Secret | Value |
|--------|--------|
| `DATABASE_URL` | Render **External** PostgreSQL URL |
| `DJANGO_SECRET_KEY` | Same as Render web service |
| `GH_PAT` | GitHub PAT with `repo` + `workflow` scope (both repos) |

Create PAT: GitHub → Settings → Developer settings → Personal access tokens.

### Auto-trigger from Render on data change

Add to Render **Environment**:

```env
GITHUB_RETRAIN=true
GITHUB_TOKEN=ghp_your_pat_here
GITHUB_REPOSITORY=letuscode293/GDSS2026_web
```

When users add/import data, the app starts the GitHub Actions retrain workflow.

---

## Deploy on Render

| Setting | Value |
|---------|--------|
| **Build command** | `./build.sh` |
| **Start command** | `./start.sh` |

```env
DATABASE_URL=postgresql://...
DJANGO_SECRET_KEY=your-secret
DEBUG=false
AUTO_PIPELINE=false
GITHUB_RETRAIN=true
GITHUB_TOKEN=ghp_...
PYTHON_VERSION=3.11.9
```

---

## Local development

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py load_datasets
python manage.py runserver 8001
```

## Monorepo (local full pipeline)

With `AUTO_PIPELINE=true` in the full project:

1. Export to `datasets/*.csv`
2. Run `scripts/train_tabular.py`
3. Reload FastAPI via `POST /reload-models`
