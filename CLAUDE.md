# Gym Recorder

A mobile-first PWA that parses handwritten gym notebook photos and saves workout data to Google Sheets.

## Architecture

- **Backend**: FastAPI (`app/main.py`) served via uvicorn
- **Frontend**: Single-page PWA (`frontend/index.html`) — no build tools, no framework
- **Image parsing**: Claude API (`app/claude_parser.py`) — sends photo, gets structured workout data back
- **Storage**: Google Sheets via service account (`app/sheets_client.py`)
- **Deployment**: Render (free tier, Oregon region) — see `render.yaml`

## Running Locally

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

App runs at http://localhost:8000.

## Environment Variables

Required in `.env` for local dev (never commit this file):

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key for image parsing |
| `GOOGLE_SHEET_ID` | ID of the target Google Sheet |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full service account JSON as a string |
| `UPLOAD_TOKEN` | Secret passphrase to protect the upload endpoint |

All four must also be set in Render's Environment dashboard for production.

## Key Files

| File | Purpose |
|---|---|
| `app/main.py` | FastAPI routes — `/health`, `/upload` |
| `app/claude_parser.py` | Sends image to Claude, returns `WorkoutRecord` |
| `app/sheets_client.py` | Reads/writes Google Sheets |
| `app/models.py` | Pydantic models: `WorkoutRecord`, `ExerciseRecord`, etc. |
| `frontend/index.html` | Entire frontend — upload UI, token auth, PWA |
| `frontend/sw.js` | Service worker for PWA |

## Google Sheets Column Layout (A:R)

| Col | Field |
|---|---|
| A | Date |
| B | Workout Name |
| C | Muscle Groups (comma-separated) |
| D | Water (oz) |
| E | Sleep (hours) |
| F | Bodyweight (lbs) |
| G | Duration (minutes) |
| H | Rating (%) |
| I | Notes |
| J | Exercise Name |
| K | Set Number |
| L | Weight (lbs) |
| M | Reps |
| N | Exercise Notes |
| O | Cardio Name |
| P | Cardio Duration (min) |
| Q | Distance (miles) |
| R | Calories |

One row per exercise set or cardio item. Base workout info (A–I) repeats on every row.

## Auth

The `/upload` endpoint requires an `X-Upload-Token` header matching the `UPLOAD_TOKEN` env var. The frontend stores the token in `localStorage` and prompts on first page load if missing. If a 401 is returned, the stored token is cleared and the user is re-prompted on next upload.

## Deployment

Push to `master` → Render auto-deploys. Python version is pinned to 3.12 in `render.yaml`.
