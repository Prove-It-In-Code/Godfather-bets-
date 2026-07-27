# Godfather Bets - Azure Sports Betting Predictor

Complete starter for an Azure-deployed sports betting predictor with:
- Flask backend model inference for **NFL, NBA, MLB, NHL**
- Edge detection against Vegas spreads
- Azure Functions entrypoint/deployment script
- Swift iOS API client sample
- Mock scikit-learn model loading fallback

## Project Layout

- `/backend/app.py` – Flask API (`/health`, `/predict`)
- `/backend/models.py` – model loading + mock fallback + feature vector builder
- `/function_app.py` – Azure Functions HTTP entrypoint wrapping Flask
- `/ios/SportsBettingAPI.swift` – Swift API client
- `/scripts/deploy_function.sh` – Azure deployment script
- `/requirements.txt` – Python dependencies

## API

When deployed to Azure Functions, this repository sets `host.json` `extensions.http.routePrefix` to `""`, so endpoints remain `/health` and `/predict` (no `/api` prefix).

### `GET /health`
Returns service status and supported sports.

### `POST /predict`
Example request:

```json
{
  "sport": "NFL",
  "home_team": "KC",
  "away_team": "BUF",
  "vegas_spread": -2.5,
  "features": {
    "home_win_pct": 0.72,
    "away_win_pct": 0.65,
    "home_rest_days": 7,
    "away_rest_days": 6,
    "home_injuries": 1,
    "away_injuries": 2,
    "recent_form_delta": 0.15
  }
}
```

Response includes:
- `predicted_spread`
- `prob_home_cover`
- `edge.discrepancy`
- `edge.recommendation` (`BET_HOME_SPREAD`, `BET_AWAY_SPREAD`, `NO_BET`)

## Azure Setup

### Prerequisites
- Python 3.11+
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local)

### Local install/run

```bash
pip install -r requirements.txt
python -m flask --app backend.app run --port 8000
```

### One-line deploy (from repo root)

```bash
RESOURCE_GROUP=godfather-bets-rg LOCATION=eastus STORAGE_ACCOUNT=<unique_storage_name> FUNCTION_APP=<unique_function_name> ./scripts/deploy_function.sh
```

### Alternative one-line publish (existing Function App)

```bash
func azure functionapp publish <FUNCTION_APP> --python
```

## Mock pre-trained model loading

`backend/models.py` attempts to load scikit-learn-compatible joblib files from:

- `models/nfl_model.joblib`
- `models/nba_model.joblib`
- `models/mlb_model.joblib`
- `models/nhl_model.joblib`

If a model file is missing, a deterministic sklearn-like mock model is used so the API still runs end-to-end.
