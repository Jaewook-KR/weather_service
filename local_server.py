#!/usr/bin/env python3
import json
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

from weather_service import weather_payload


class LocalHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/api/weather":
            query_params = parse_qs(parsed_url.query)
            location = query_params.get("location", ["서울"])[0].strip()

            if not location:
                self.send_json(400, {"error": "위치를 입력해 주세요."})
                return

            try:
                status, payload = weather_payload(location)
                self.send_json(status, payload)
            except Exception as exc:
                self.send_json(502, {"error": f"날씨 정보를 불러오지 못했습니다: {exc}"})
            return

        super().do_GET()

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 5000), LocalHandler)
    print("정적 웹 페이지 서버: http://127.0.0.1:5000")
    print("Vercel 배포에서는 /api/weather.py 서버리스 함수를 사용합니다.")
    server.serve_forever()


if __name__ == "__main__":
    main()
