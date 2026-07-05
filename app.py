#!/usr/bin/env python3
import sys
from pathlib import Path
from urllib.error import URLError


PROJECT_DIR = Path(__file__).resolve().parent
LOCAL_PACKAGES = PROJECT_DIR / ".python-packages"

if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

from flask import Flask, jsonify, send_from_directory, request

from api.weather import weather_payload


app = Flask(__name__, static_folder="static", static_url_path="/static")


@app.get("/")
def index():
    return send_from_directory(".", "index.html")


@app.get("/api/weather")
def weather():
    location = request.args.get("location", "서울").strip()

    if not location:
        return jsonify({"error": "위치를 입력해 주세요."}), 400

    try:
        status, payload = weather_payload(location)
        return jsonify(payload), status
    except (KeyError, URLError, TimeoutError, ValueError) as exc:
        return jsonify({"error": f"날씨 정보를 불러오지 못했습니다: {exc}"}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
