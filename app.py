
import os
import logging
import httpx

from flask import Flask, jsonify, request, send_from_directory

# ============================================================
# HNTH UID INFO API
# Flask frontend + CORS-free same-origin API proxy
# No Firebase, no login, no separate api folder
# ============================================================

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPSTREAM_API = (
    "https://api-info-tz3o-cy8wp8cz3-"
    "developer-hntgs-projects.vercel.app"
).rstrip("/")

TIMEOUT = httpx.Timeout(20.0, connect=8.0)


@app.get("/")
def home():
    """Serve the frontend if index.html exists."""
    if os.path.isfile(os.path.join(BASE_DIR, "index.html")):
        return send_from_directory(BASE_DIR, "index.html")

    base_url = request.url_root.rstrip("/")
    return jsonify({
        "status": "ok",
        "service": "HNTH UID Info API",
        "message": "API is online",
        "base_url": base_url,
        "endpoints": {
            "health": f"{base_url}/api/health",
            "player_lookup": (
                f"{base_url}/api/player?uid=PLAYER_UID&key=HNTH"
            )
        }
    })


@app.get("/api/health")
def health():
    """Check this deployment and its upstream configuration."""
    return jsonify({
        "status": "ok",
        "service": "HNTH UID Info API",
        "proxy": "configured",
        "upstream": UPSTREAM_API
    })


@app.get("/api/player")
def player():
    """
    Proxy a player lookup through the working HNTH API.

    Example:
    /api/player?uid=1871114586&key=HNTH
    """
    uid = (request.args.get("uid") or "").strip()
    api_key = (request.args.get("key") or "HNTH").strip()

    if not uid or not uid.isdigit() or len(uid) < 4:
        return jsonify({
            "status": "error",
            "error": "Invalid UID",
            "message": "Enter a valid numeric player UID."
        }), 400

    if not api_key:
        return jsonify({
            "status": "error",
            "error": "Missing API key",
            "message": "The key parameter is required."
        }), 400

    # Forward optional parameters only when supplied.
    params = {
        "uid": uid,
        "key": api_key
    }

    for name in ("game", "region"):
        value = (request.args.get(name) or "").strip()
        if value:
            params[name] = value

    upstream_url = f"{UPSTREAM_API}/api/player"

    try:
        with httpx.Client(
            timeout=TIMEOUT,
            follow_redirects=True
        ) as client:
            upstream = client.get(
                upstream_url,
                params=params,
                headers={"Accept": "application/json"}
            )

        # Preserve the upstream response body and HTTP status.
        try:
            data = upstream.json()
        except ValueError:
            app.logger.error(
                "Upstream returned non-JSON response (HTTP %s)",
                upstream.status_code
            )
            return jsonify({
                "status": "error",
                "error": "Invalid upstream response",
                "message": "The player API returned an unexpected response."
            }), 502

        return jsonify(data), upstream.status_code

    except httpx.TimeoutException:
        app.logger.warning("Player API request timed out for UID %s", uid)
        return jsonify({
            "status": "error",
            "error": "Upstream timeout",
            "message": "The player API took too long to respond."
        }), 504

    except httpx.RequestError:
        app.logger.exception("Could not connect to upstream player API")
        return jsonify({
            "status": "error",
            "error": "Upstream unavailable",
            "message": "Could not connect to the player API."
        }), 502


@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "status": "error",
        "error": "Not found",
        "available_endpoints": [
            "/",
            "/api/health",
            "/api/player?uid=PLAYER_UID&key=HNTH"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(_error):
    app.logger.exception("Unexpected server error")
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500


# Vercel detects the Flask WSGI application named "app".
# Do not add app.run() for deployment.
