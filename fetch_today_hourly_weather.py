#!/usr/bin/env python3
import argparse
import json
import os
import ssl
import sys
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def fetch_hourly_weather(latitude, longitude, timezone):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": ",".join(
            [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "weather_code",
                "wind_speed_10m",
            ]
        ),
        "timezone": timezone,
        "forecast_days": 1,
    }
    url = "https://api.open-meteo.com/v1/forecast?" + urlencode(params)
    ssl_context = None

    if os.path.exists("/etc/ssl/cert.pem"):
        ssl_context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")

    with urlopen(url, timeout=10, context=ssl_context) as response:
        return json.load(response)


def print_hourly_weather(data):
    hourly = data["hourly"]
    units = data.get("hourly_units", {})

    print("Time              Temp      Humidity  Rain      Wind      Weather")
    print("-" * 78)

    for i, time_text in enumerate(hourly["time"]):
        weather_code = hourly["weather_code"][i]
        weather = WEATHER_CODES.get(weather_code, f"Code {weather_code}")

        print(
            f"{time_text:<17} "
            f"{hourly['temperature_2m'][i]:>5} {units.get('temperature_2m', ''):<4} "
            f"{hourly['relative_humidity_2m'][i]:>7} {units.get('relative_humidity_2m', ''):<3} "
            f"{hourly['precipitation'][i]:>5} {units.get('precipitation', ''):<4} "
            f"{hourly['wind_speed_10m'][i]:>5} {units.get('wind_speed_10m', ''):<5} "
            f"{weather}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Fetch today's hourly weather from the Open-Meteo API."
    )
    parser.add_argument("--latitude", type=float, default=37.5665, help="Default: Seoul")
    parser.add_argument("--longitude", type=float, default=126.9780, help="Default: Seoul")
    parser.add_argument("--timezone", default="Asia/Seoul", help="Default: Asia/Seoul")
    args = parser.parse_args()

    try:
        data = fetch_hourly_weather(args.latitude, args.longitude, args.timezone)
    except URLError as error:
        print(f"Open-Meteo API request failed: {error}", file=sys.stderr)
        sys.exit(1)

    print_hourly_weather(data)


if __name__ == "__main__":
    main()
