# HNTH Simple UID Info API

Minimal Flask API, without Firebase, login, dashboard, or an `api/` folder.
No `UPSTREAM_KEY` environment variable is required.

## Files
- `app.py` — complete Flask API
- `index.py` — compatibility import
- `vercel.json` — routes requests to `app.py`
- `requirements.txt` — Python dependencies

## Deploy
1. Put all files at the root of your GitHub repository.
2. Import the repository in Vercel and set Root Directory to the repository root.
3. Deploy. No `UPSTREAM_KEY` environment variable is needed.
4. If your upstream provider uses a different endpoint, set `UPSTREAM_URL` in Vercel (optional; default is `https://apiv2.mlbbshop.com/ign`).

## Endpoints
- `GET /` — service information and example URLs
- `GET /api/health` — health check
- `GET /api/player?uid=1871114586&key=HNTH` — player lookup

The `key` query parameter is forwarded to the upstream provider. `HNTH` must be a valid key for that provider for lookups to succeed. This removes the Vercel `UPSTREAM_KEY` setting, but it cannot bypass authentication required by the upstream service.
