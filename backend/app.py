from __future__ import annotations

from flask import Flask, jsonify, request

from .models import DEFAULT_FEATURE_ORDER, SUPPORTED_SPORTS, build_feature_vector, load_model

EDGE_THRESHOLD = 1.5

app = Flask(__name__)


def compute_edge(predicted_spread: float, vegas_spread: float, threshold: float = EDGE_THRESHOLD) -> dict:
    discrepancy = predicted_spread - vegas_spread
    if discrepancy <= -threshold:
        recommendation = "BET_HOME_SPREAD"
    elif discrepancy >= threshold:
        recommendation = "BET_AWAY_SPREAD"
    else:
        recommendation = "NO_BET"

    return {
        "discrepancy": round(discrepancy, 3),
        "threshold": threshold,
        "recommendation": recommendation,
        "confidence": round(min(abs(discrepancy) / (threshold * 2), 1.0), 3),
    }


@app.get("/health")
def health() -> tuple:
    return jsonify({"status": "ok", "sports": sorted(SUPPORTED_SPORTS)}), 200


@app.post("/predict")
def predict() -> tuple:
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "request body must be a JSON object"}), 400

    sport = str(payload.get("sport", "")).upper()
    if sport not in SUPPORTED_SPORTS:
        return jsonify({"error": f"sport must be one of {sorted(SUPPORTED_SPORTS)}"}), 400

    try:
        vegas_spread = float(payload["vegas_spread"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "vegas_spread is required and must be numeric"}), 400

    features = payload.get("features") or {}
    if not isinstance(features, dict):
        return jsonify({"error": "features must be an object"}), 400

    model = load_model(sport)
    feature_vector = build_feature_vector(features, DEFAULT_FEATURE_ORDER)
    prob_home_cover = float(model.predict_proba(feature_vector)[0][1])

    # Convert cover probability into a model-implied spread in vegas convention.
    implied_shift = (prob_home_cover - 0.5) * 8.0
    predicted_spread = vegas_spread - implied_shift

    edge = compute_edge(predicted_spread=predicted_spread, vegas_spread=vegas_spread)

    response = {
        "sport": sport,
        "home_team": payload.get("home_team"),
        "away_team": payload.get("away_team"),
        "vegas_spread": vegas_spread,
        "predicted_spread": round(predicted_spread, 3),
        "prob_home_cover": round(prob_home_cover, 4),
        "edge": edge,
        "feature_order": DEFAULT_FEATURE_ORDER,
    }
    return jsonify(response), 200
