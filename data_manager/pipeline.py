import logging
import subprocess
import sys
from pathlib import Path

import requests
from django.conf import settings

from .github_dispatch import trigger_retrain_workflow
from .services import write_exports_to_datasets

logger = logging.getLogger(__name__)


def run_full_pipeline() -> tuple[bool, str]:
    """Export DB → retrain via GitHub Actions or local ml_pipeline."""
    if not settings.AUTO_PIPELINE and not settings.GITHUB_RETRAIN:
        return True, "Automation disabled."

    write_exports_to_datasets()

    if settings.GITHUB_RETRAIN:
        return trigger_retrain_workflow()

    ml_root = Path(settings.ML_PIPELINE_ROOT)
    train_script = ml_root / "scripts" / "train_tabular.py"
    if not train_script.exists():
        return True, "Data exported. ml_pipeline not found — training skipped."

    # Sync exported CSVs into ml_pipeline/datasets for training
    for name in ("Crop_recommendation.csv", "Fertilizer_Prediction.csv"):
        src = settings.DATASETS_DIR / name
        dst = ml_root / "datasets" / name
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(train_script)],
        capture_output=True,
        text=True,
        cwd=ml_root,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "Training failed."
        logger.error("Training failed: %s", detail)
        return False, detail

    reload_msg = _reload_api()
    output = result.stdout.strip()
    return True, f"{output}\n{reload_msg}".strip()


def _reload_api() -> str:
    try:
        response = requests.post(settings.API_RELOAD_URL, timeout=60)
        response.raise_for_status()
        return "API models reloaded."
    except requests.RequestException as exc:
        logger.warning("Could not reload API: %s", exc)
        return "Models trained. Start the API to serve updated predictions."
