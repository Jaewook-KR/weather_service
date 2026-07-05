# 날씨 검색 웹 페이지 실행 및 Vercel 배포 방법

이 프로젝트는 Flask 앱으로 실행됩니다. Flask가 정적 HTML/CSS/JavaScript 페이지와 `/api/weather` API를 제공하고, Open-Meteo API로 오늘 시간별 날씨를 가져온 뒤 브라우저에서 SVG 그래프로 표시합니다.

## 로컬 실행

### 1. 프로젝트 폴더로 이동

```bash
cd /Users/jaewook/Desktop/agent_demo
```

### 2. 필요한 패키지 설치

Flask가 필요합니다. 로컬에 이미 설치되어 있지 않다면 아래 명령을 실행하세요.

```bash
python3 -m pip install --target .python-packages Flask
```

### 3. 로컬 서버 실행

```bash
python3 app.py
```

서버가 실행되면 브라우저에서 아래 주소를 엽니다.

```text
http://127.0.0.1:5000
```

### 4. 사용 방법

검색창에 `서울`, `부산`, `Tokyo`, `New York`처럼 위치를 입력하고 `검색` 버튼을 누르면 오늘 시간별 기온 그래프와 날씨 표가 표시됩니다.

## Vercel 배포

Vercel 배포를 위해 아래 파일을 추가했습니다.

- `public/index.html`: Vercel에서 CDN으로 제공되는 정적 웹 페이지
- `public/static/app.js`: 위치 검색, API 호출, SVG 그래프 렌더링
- `public/static/styles.css`: 화면 스타일
- `app.py`: Flask 앱 진입점
- `weather_service.py`: Flask 라우트에서 재사용하는 날씨 조회 로직
- `vercel.json`: 모든 요청을 Flask 앱으로 전달하는 설정
- `requirements.txt`: Vercel에서 설치할 Python 패키지 목록
- `.vercelignore`: 로컬 전용 패키지와 캐시 파일 업로드 제외

### 1. Vercel CLI 설치

```bash
npm install -g vercel
```

### 2. Vercel 로그인

```bash
vercel login
```

### 3. 배포

프로젝트 폴더에서 아래 명령을 실행합니다.

```bash
vercel
```

처음 배포할 때 나오는 질문은 일반적으로 기본값으로 진행하면 됩니다.

### 4. 운영 배포

미리보기 배포가 정상 동작하면 운영 주소로 배포합니다.

```bash
vercel --prod
```

## Vercel 설정 참고

이 앱은 Open-Meteo 공개 API만 사용하므로 별도의 API 키나 환경 변수는 필요하지 않습니다.

Vercel은 루트의 `app.py`에서 top-level `app` 변수를 Flask/WSGI 앱으로 인식합니다. 이전 배포 오류를 피하기 위해 `app.py`는 반드시 `app = Flask(...)`를 export합니다.

Vercel의 Flask 문서에서는 정적 파일을 `public/**`에 두도록 안내합니다. 그래서 웹 페이지 파일은 `public` 폴더에 두고, Flask 함수는 `/api/weather` 요청을 처리합니다.

그래프는 서버에서 이미지 파일로 만들지 않고 브라우저에서 SVG로 그립니다. 그래서 Vercel 배포에는 Matplotlib이 필요하지 않습니다.

## 참고

Open-Meteo API를 사용하므로 인터넷 연결이 필요합니다. macOS Python에서 로컬 실행 중 SSL 인증서 오류가 발생하면 Python 설치 폴더의 `Install Certificates.command`를 한 번 실행한 뒤 다시 서버를 실행하세요.
