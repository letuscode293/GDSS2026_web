"""Trigger GitHub Actions retrain workflow from the Django app."""
import logging
import os

import requests

logger = logging.getLogger(__name__)


def trigger_retrain_workflow() -> tuple[bool, str]:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT")
    repo = os.environ.get("GITHUB_REPOSITORY", "letuscode293/GDSS2026_web")
    workflow_file = os.environ.get(
        "GITHUB_WORKFLOW_FILE", "retrain-from-database.yml"
    )

    if not token:
        return False, "GITHUB_TOKEN not set — cannot trigger retrain workflow."

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    dispatch_url = (
        f"https://api.github.com/repos/{repo}/actions/workflows/"
        f"{workflow_file}/dispatches"
    )
    response = requests.post(
        dispatch_url,
        headers=headers,
        json={"ref": os.environ.get("GITHUB_REF", "richard")},
        timeout=30,
    )

    if response.status_code == 204:
        return True, "GitHub Actions retrain workflow started."

    logger.error("GitHub dispatch failed: %s %s", response.status_code, response.text)
    return False, f"GitHub dispatch failed ({response.status_code})."
