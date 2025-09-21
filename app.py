import os
import time
import logging
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import updream_crawler as crawler

# Set up logger configuration
# The logger will print to both a file and the console.
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

def run_scheduler():
    """Initializes and starts the background scheduler."""
    # This condition prevents the scheduler from running twice in debug mode
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        logger.info("Scheduler for crawling is registered.")
        scheduler = BackgroundScheduler()
        # Run the crawl job every minute
        scheduler.add_job(func=crawler.scheduled_crawl_job, trigger="interval", minutes=120)
        scheduler.start()
        logger.info("Scheduler started in the background.")

@app.route('/')
def home():
    """Home page for health check."""
    logger.info("Home page accessed.")
    return "Hello, the Flask app is running correctly."

@app.route('/deliveries')
def get_deliveries():
    import mysql.connector, os
    conn = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"]
    )
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT tracking_number, status, recipient_info, crawled_at FROM delivery ORDER BY crawled_at DESC LIMIT 20")
    rows = cur.fetchall()
    conn.close()
    return {"deliveries": rows}

# Run the scheduler when the Flask app starts
if __name__ == '__main__':
    run_scheduler()
    try:
        logger.info("Flask app starting...")
        app.run(host='0.0.0.0', port=5002)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Flask app is shutting down.")
        pass
