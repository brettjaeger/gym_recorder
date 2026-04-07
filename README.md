# Gym Recorder

A mobile-first PWA that photographs handwritten gym notebook pages and automatically parses them into a Google Sheet using Claude's vision API.

## Notebook

This app is designed to work with [this notebook](https://www.amazon.com/dp/B0BG7WY5BW?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1).

## How it works

1. Open the app on your phone and take a photo of your workout notebook page
2. The image is sent to the backend, which uses Claude to extract structured workout data
3. The data is appended to a Google Sheet — one row per exercise set or cardio item

## Stack

- **Backend**: FastAPI + uvicorn
- **Frontend**: Single HTML file, no framework, installable as a PWA
- **Parsing**: Claude API (vision)
- **Storage**: Google Sheets (service account)
- **Deployment**: Render (free tier)

## Running locally

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

App runs at http://localhost:8000.

Create a `.env` file with the following variables:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Claude API key for image parsing |
| `GOOGLE_SHEET_ID` | ID of the target Google Sheet |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Full service account JSON as a string |
| `UPLOAD_TOKEN` | Secret passphrase to protect the upload endpoint |

## Deployment

Push to `master` — Render auto-deploys. Python 3.12 is pinned in `render.yaml`.

Set all four environment variables in the Render dashboard.

## Google Sheets layout

One row per exercise set or cardio item. Workout metadata (date, name, bodyweight, etc.) repeats on every row.

| A    | B            | C             | D          | E             | F                | G              | H          | I     | J             | K          | L            | M    | N              | O           | P                     | Q                | R        |
|------|--------------|---------------|------------|---------------|------------------|----------------|------------|-------|---------------|------------|--------------|------|----------------|-------------|-----------------------|------------------|----------|
| Date | Workout Name | Muscle Groups | Water (oz) | Sleep (hours) | Bodyweight (lbs) | Duration (min) | Rating (%) | Notes | Exercise Name | Set Number | Weight (lbs) | Reps | Exercise Notes | Cardio Name | Cardio Duration (min) | Distance (miles) | Calories |

## Auth

The `/upload` endpoint requires an `X-Upload-Token` header. The frontend prompts for the token on first load and stores it in `localStorage`. A 401 response clears the stored token and re-prompts on next upload.
