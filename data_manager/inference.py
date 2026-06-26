"""Crop and fertilizer predictions — local models or remote API."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import joblib
import numpy as np
import requests
from django.conf import settings

CROP_FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
FERT_NUMERIC = ["Temparature", "Humidity ", "Moisture", "Nitrogen", "Potassium", "Phosphorous"]
FERT_CATEGORICAL = ["Soil Type", "Crop Type"]
FERT_FEATURES = FERT_NUMERIC + FERT_CATEGORICAL


def _api_base() -> str | None:
    raw = os.environ.get("GDSS2026_API_URL", "").strip().rstrip("/")
    if not raw:
        return None
    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"
    return raw


@dataclass
class LocalModels:
    crop_model: object | None = None
    crop_scaler: object | None = None
    crop_encoder: object | None = None
    fert_model: object | None = None
    fert_scaler: object | None = None
    fert_encoder: object | None = None
    fert_cat_encoders: dict | None = None
    errors: dict[str, str] = field(default_factory=dict)

    def load_all(self) -> None:
        models_dir = Path(settings.MODELS_DIR)
        try:
            self.crop_model = joblib.load(models_dir / "crop_recommendation_model.pkl")
            self.crop_scaler = joblib.load(models_dir / "crop_scaler.pkl")
            self.crop_encoder = joblib.load(models_dir / "crop_label_encoder.pkl")
        except Exception as exc:
            self.errors["crop"] = str(exc)

        try:
            self.fert_model = joblib.load(models_dir / "fertilizer_recommendation_model.pkl")
            self.fert_scaler = joblib.load(models_dir / "fert_scaler.pkl")
            self.fert_encoder = joblib.load(models_dir / "fert_label_encoder.pkl")
            self.fert_cat_encoders = joblib.load(models_dir / "fert_categorical_encoders.pkl")
        except Exception as exc:
            self.errors["fertilizer"] = str(exc)

    def predict_crop(self, features: dict) -> tuple[str, float]:
        if not self.crop_model:
            raise RuntimeError(self.errors.get("crop", "Crop model not loaded"))
        row = np.array([[features[k] for k in CROP_FEATURES]])
        scaled = self.crop_scaler.transform(row)
        proba = self.crop_model.predict_proba(scaled)[0]
        idx = int(np.argmax(proba))
        return self.crop_encoder.classes_[idx], float(proba[idx])

    def predict_fertilizer(self, features: dict) -> tuple[str, float]:
        if not self.fert_model:
            raise RuntimeError(self.errors.get("fertilizer", "Fertilizer model not loaded"))
        row = features.copy()
        for col, encoder in self.fert_cat_encoders.items():
            row[col] = encoder.transform([row[col]])[0]
        matrix = np.array([[row[k] for k in FERT_FEATURES]])
        scaled = self.fert_scaler.transform(matrix)
        proba = self.fert_model.predict_proba(scaled)[0]
        idx = int(np.argmax(proba))
        return self.fert_encoder.classes_[idx], float(proba[idx])


@lru_cache(maxsize=1)
def _local_models() -> LocalModels:
    registry = LocalModels()
    registry.load_all()
    return registry


def reload_local_models() -> None:
    _local_models.cache_clear()
    _local_models()


def predict_crop(features: dict) -> tuple[str, float]:
    api = _api_base()
    if api:
        response = requests.post(f"{api}/predict/crop", json=features, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["crop"], float(data["confidence"])

    mapped = {
        "N": features["n"],
        "P": features["p"],
        "K": features["k"],
        "temperature": features["temperature"],
        "humidity": features["humidity"],
        "ph": features["ph"],
        "rainfall": features["rainfall"],
    }
    return _local_models().predict_crop(mapped)


def predict_fertilizer(features: dict) -> tuple[str, float]:
    api = _api_base()
    if api:
        payload = {
            "temperature": features["temperature"],
            "humidity": features["humidity"],
            "moisture": features["moisture"],
            "soil_type": features["soil_type"],
            "crop_type": features["crop_type"],
            "nitrogen": features["nitrogen"],
            "potassium": features["potassium"],
            "phosphorous": features["phosphorous"],
        }
        response = requests.post(f"{api}/predict/fertilizer", json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data["fertilizer"], float(data["confidence"])

    mapped = {
        "Temparature": features["temperature"],
        "Humidity ": features["humidity"],
        "Moisture": features["moisture"],
        "Soil Type": features["soil_type"],
        "Crop Type": features["crop_type"],
        "Nitrogen": features["nitrogen"],
        "Potassium": features["potassium"],
        "Phosphorous": features["phosphorous"],
    }
    return _local_models().predict_fertilizer(mapped)


def models_ready() -> dict[str, bool]:
    if _api_base():
        try:
            response = requests.get(f"{_api_base()}/health", timeout=15)
            response.raise_for_status()
            return response.json().get("models_loaded", {})
        except requests.RequestException:
            return {"crop": False, "fertilizer": False}

    local = _local_models()
    return {
        "crop": local.crop_model is not None,
        "fertilizer": local.fert_model is not None,
    }
