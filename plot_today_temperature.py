#!/usr/bin/env python3
import argparse
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.error import URLError


PROJECT_DIR = Path(__file__).resolve().parent
LOCAL_PACKAGES = PROJECT_DIR / ".python-packages"

if LOCAL_PACKAGES.exists():
    sys.path.insert(0, str(LOCAL_PACKAGES))

DEFAULT_MPLCONFIGDIR = "/tmp/matplotlib-cache" if os.environ.get("VERCEL") else str(PROJECT_DIR / ".matplotlib-cache")
os.environ.setdefault("MPLCONFIGDIR", DEFAULT_MPLCONFIGDIR)

import matplotlib
import matplotlib.font_manager as font_manager

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from fetch_today_hourly_weather import fetch_hourly_weather


def parse_hourly_temperature(data):
    hourly = data["hourly"]
    times = [datetime.fromisoformat(value) for value in hourly["time"]]
    temperatures = hourly["temperature_2m"]
    unit = data.get("hourly_units", {}).get("temperature_2m", "C")
    return times, temperatures, unit


def configure_korean_font():
    preferred_fonts = ["AppleGothic", "Malgun Gothic", "NanumGothic", "Noto Sans CJK KR"]
    available_fonts = {font.name for font in font_manager.fontManager.ttflist}

    for font_name in preferred_fonts:
        if font_name in available_fonts:
            plt.rcParams["font.family"] = font_name
            break

    plt.rcParams["axes.unicode_minus"] = False


def save_temperature_chart(times, temperatures, unit, output_path, location_name="서울"):
    configure_korean_font()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(times, temperatures, marker="o", linewidth=2.2, color="#2563eb")
    ax.fill_between(times, temperatures, min(temperatures) - 1, color="#93c5fd", alpha=0.25)

    ax.set_title(f"오늘 시간별 기온 - {location_name}", fontsize=16, pad=14)
    ax.set_xlabel("시간")
    ax.set_ylabel(f"기온 ({unit})")
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.45)
    ax.set_xticks(times)
    ax.set_xticklabels([time.strftime("%H:%M") for time in times], rotation=45, ha="right")

    min_temp = min(temperatures)
    max_temp = max(temperatures)
    ax.set_ylim(min_temp - 1, max_temp + 1)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160, format="png")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch today's Open-Meteo hourly temperature and save it as a chart."
    )
    parser.add_argument("--latitude", type=float, default=37.5665, help="Default: Seoul")
    parser.add_argument("--longitude", type=float, default=126.9780, help="Default: Seoul")
    parser.add_argument("--timezone", default="Asia/Seoul", help="Default: Asia/Seoul")
    parser.add_argument(
        "--output",
        default="today_temperature.png",
        help="Output image path. Default: today_temperature.png",
    )
    args = parser.parse_args()

    try:
        data = fetch_hourly_weather(args.latitude, args.longitude, args.timezone)
    except URLError as error:
        print(f"Open-Meteo API request failed: {error}", file=sys.stderr)
        sys.exit(1)

    times, temperatures, unit = parse_hourly_temperature(data)
    save_temperature_chart(times, temperatures, unit, args.output)
    print(f"Saved chart to {args.output}")


if __name__ == "__main__":
    main()
