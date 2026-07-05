import json
import os
import ssl
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

from fetch_today_hourly_weather import WEATHER_CODES, fetch_hourly_weather


LOCATION_ALIASES = {
    "서울": "Seoul",
    "서울시": "Seoul",
    "서울특별시": "Seoul",
    "부산": "Busan",
    "부산광역시": "Busan",
    "인천": "Incheon",
    "인천광역시": "Incheon",
    "대구": "Daegu",
    "대구광역시": "Daegu",
    "대전": "Daejeon",
    "대전광역시": "Daejeon",
    "광주": "Gwangju",
    "광주광역시": "Gwangju",
    "울산": "Ulsan",
    "울산광역시": "Ulsan",
    "세종": "Sejong",
    "세종시": "Sejong",
    "제주": "Jeju",
    "제주시": "Jeju",
    "수원": "Suwon",
    "성남": "Seongnam",
    "고양": "Goyang",
    "용인": "Yongin",
    "청주": "Cheongju",
    "전주": "Jeonju",
    "천안": "Cheonan",
    "포항": "Pohang",
    "창원": "Changwon",
    "김해": "Gimhae",
}


WEATHER_CODE_KO = {
    0: "맑음",
    1: "대체로 맑음",
    2: "부분적으로 흐림",
    3: "흐림",
    45: "안개",
    48: "서리 안개",
    51: "약한 이슬비",
    53: "보통 이슬비",
    55: "강한 이슬비",
    61: "약한 비",
    63: "보통 비",
    65: "강한 비",
    71: "약한 눈",
    73: "보통 눈",
    75: "강한 눈",
    80: "약한 소나기",
    81: "보통 소나기",
    82: "강한 소나기",
    95: "뇌우",
    96: "약한 우박을 동반한 뇌우",
    99: "강한 우박을 동반한 뇌우",
}


def ssl_context():
    if os.path.exists("/etc/ssl/cert.pem"):
        return ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    return None


def fetch_json(url):
    with urlopen(url, timeout=10, context=ssl_context()) as response:
        return json.load(response)


def search_location(query):
    search_query = LOCATION_ALIASES.get(query, query)
    params = {
        "name": search_query,
        "count": 1,
        "language": "ko",
        "format": "json",
    }
    url = "https://geocoding-api.open-meteo.com/v1/search?" + urlencode(params)
    data = fetch_json(url)
    results = data.get("results", [])

    if not results:
        return None

    result = results[0]
    parts = [result.get("name"), result.get("admin1"), result.get("country")]

    return {
        "name": ", ".join(part for part in parts if part),
        "latitude": result["latitude"],
        "longitude": result["longitude"],
        "timezone": result.get("timezone", "auto"),
    }


def weather_rows(data):
    hourly = data["hourly"]
    units = data.get("hourly_units", {})
    rows = []

    for index, time_text in enumerate(hourly["time"]):
        weather_code = hourly["weather_code"][index]
        rows.append(
            {
                "time": datetime.fromisoformat(time_text).strftime("%H:%M"),
                "temperature": hourly["temperature_2m"][index],
                "temperatureUnit": units.get("temperature_2m", "°C"),
                "humidity": hourly["relative_humidity_2m"][index],
                "humidityUnit": units.get("relative_humidity_2m", "%"),
                "precipitation": hourly["precipitation"][index],
                "precipitationUnit": units.get("precipitation", "mm"),
                "windSpeed": hourly["wind_speed_10m"][index],
                "windSpeedUnit": units.get("wind_speed_10m", "km/h"),
                "weather": WEATHER_CODE_KO.get(
                    weather_code,
                    WEATHER_CODES.get(weather_code, f"날씨 코드 {weather_code}"),
                ),
            }
        )

    return rows


def weather_payload(query):
    location = search_location(query)

    if location is None:
        return 404, {"error": f"'{query}'에 해당하는 위치를 찾지 못했습니다."}

    weather_data = fetch_hourly_weather(
        location["latitude"],
        location["longitude"],
        location["timezone"],
    )
    rows = weather_rows(weather_data)
    temperatures = [row["temperature"] for row in rows]

    return 200, {
        "location": location,
        "timezone": weather_data.get("timezone", location["timezone"]),
        "minTemperature": min(temperatures),
        "maxTemperature": max(temperatures),
        "rows": rows,
    }
