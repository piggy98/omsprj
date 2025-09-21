FROM python:3.9-slim

#작업 디렉터리 설정
WORKDIR /app

#requirements.txt 파일을 컨테이너에 복사
COPY requirements.txt .

#필요한 파이썬 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

#파이썬 스크립트 파일 복사
COPY updream_crawler.py .
COPY app.py .

#스크립트 실행 (Flask 앱)
CMD ["python", "app.py"]
