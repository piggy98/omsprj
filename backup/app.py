import os
import logging
from flask import Flask, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import mysql.connector
import updream_crawler as crawler

# ---------------------------
# Logger 설정 (STDOUT 중심)
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ---------------------------
# Flask 앱 생성
# ---------------------------
app = Flask(__name__)

# ---------------------------
# 스케줄러 실행 함수
# ---------------------------
def run_scheduler():
    """Initializes and starts the background scheduler."""
    interval = int(os.environ.get("CRAWL_INTERVAL_MINUTES", "120"))
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=crawler.scheduled_crawl_job,
        trigger="interval",
        minutes=interval
    )
    scheduler.start()
    logger.info(f"Scheduler started: runs every {interval} minutes.")

# ---------------------------
# 라우트
# ---------------------------
@app.route('/')
def home():
    """Health check endpoint."""
    logger.info("Health check endpoint hit.")
    return "Hello, the Flask app is running correctly."

@app.route('/deliveries')
def get_deliveries():
    """최근 크롤링 결과를 반환하는 엔드포인트 (JSON)"""
    try:
        conn = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"]
        )
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT tracking_number, status, recipient_info, crawled_at "
            "FROM delivery ORDER BY crawled_at DESC LIMIT 20"
        )
        rows = cur.fetchall()
        conn.close()
        return jsonify(rows)
    except Exception as e:
        logger.error(f"Error fetching deliveries: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------
# 메인 실행부
# ---------------------------
if __name__ == '__main__':
    run_scheduler()
    try:
        logger.info("Flask app starting...")
        app.run(host='0.0.0.0', port=5002)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Flask app is shutting down.")
