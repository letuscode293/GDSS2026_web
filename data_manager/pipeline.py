import logging
import subprocess
import sys
from pathlib import Path

import requests
from django.conf import settings

from .services import write_exports_to_datasets

logger = logging.getLogger(__name__)


def run_full_pipeline() -> tuple[bool, str]:
    """Export DB → retrain models → reload API. Used after data changes."""
    if not settings.AUTO_PIPELINE:
        return True, "Automation disabled."

    write_exports_to_datasets()

    train_script = Path(settings.PROJECT_ROOT) / "scripts" / "train_tabular.py"
    result = subprocess.run(
        [sys.executable, str(train_script)],
        capture_output=True,
        text=True,
        cwd=settings.PROJECT_ROOT,
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
