from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Dict, List

import joblib
import numpy as np

SUPPORTED_SPORTS = {"NFL", "NBA", "MLB", "NHL"}
MODEL_FILES = {
    "NFL": "nfl_model.joblib",
    "NBA": "nba_model.joblib",
    "MLB": "mlb_model.joblib",
    "NHL": "nhl_model.joblib",
}
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
DEFAULT_FEATURE_ORDER = [
    "home_win_pct",
    "away_win_pct",
    "home_rest_days",
    "away_rest_days",
    "home_injuries",
    "away_injuries",
    "recent_form_delta",
]


class MockSklearnModel:
    """Sklearn-like fallback model that exposes predict_proba."""

    def __init__(self, sport: str):
        self.sport = sport
        self.classes_ = np.array([0, 1])

    def predict_proba(self, x: np.ndarray) -> np.ndarray:
        # lightweight deterministic heuristic by sport
        weights = {
            "NFL": np.array([0.35, -0.35, 0.12, -0.12, -0.15, 0.15, 0.2]),
            "NBA": np.array([0.4, -0.4, 0.08, -0.08, -0.1, 0.1, 0.25]),
            "MLB": np.array([0.28, -0.28, 0.05, -0.05, -0.07, 0.07, 0.18]),
            "NHL": np.array([0.3, -0.3, 0.09, -0.09, -0.09, 0.09, 0.2]),
        }[self.sport]
        margin = float(np.dot(x[0], weights))
        prob_home_cover = 1.0 / (1.0 + np.exp(-margin))
        return np.array([[1.0 - prob_home_cover, prob_home_cover]])


def _model_path(sport: str) -> Path:
    model_name = MODEL_FILES[sport]
    model_file = (MODEL_DIR / model_name).resolve()
    if model_file.parent != MODEL_DIR.resolve():
        raise ValueError("Model path validation failed")
    return model_file


@lru_cache(maxsize=len(SUPPORTED_SPORTS))
def load_model(sport: str):
    sport = sport.upper()
    if sport not in SUPPORTED_SPORTS:
        raise ValueError(f"Unsupported sport '{sport}'")

    model_file = _model_path(sport)
    if model_file.is_file() and model_file.suffix == ".joblib":
        # Load only from fixed, allowlisted local paths.
        return joblib.load(model_file)

    return MockSklearnModel(sport)


def build_feature_vector(features: Dict[str, float], feature_order: List[str] | None = None) -> np.ndarray:
    order = feature_order or DEFAULT_FEATURE_ORDER
    values = [float(features.get(name, 0.0)) for name in order]
    return np.array([values], dtype=float)
