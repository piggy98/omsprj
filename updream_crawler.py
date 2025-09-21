import re
import requests
import mysql.connector
import os
import time
from bs4 import BeautifulSoup
from datetime import datetime

# MariaDB 연결 정보 (환경 변수 사용)
DB_HOST = os.environ.get("DB_HOST", "mariadb")
DB_USER = os.environ.get("DB_USER", "haedam")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "1234")
DB_NAME = os.environ.get("DB_NAME", "oms")
TABLE_NAME = 'delivery'

def initialize_database():
    """Initializes the MariaDB database and creates the delivery table if it does not exist."""
    print("데이터베이스 초기화 중...", flush=True)
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                ID INT AUTO INCREASE,
                수취인명 VARCHAR(30),
                운송장번호 VARCHAR(20) PRIMARY KEY,
                발주처트랙킹번호 VARCHAR(255),
                상품번호 VARCHAR(10),
                crawled_at DATETIME
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("데이터베이스 초기화 완료.", flush=True)
    except mysql.connector.Error as e:
        print(f"MariaDB 연결 또는 초기화 오류: {e}")
        return False
    return True

def get_tracking_numbers_for_period():
    """
    Simulates fetching a list of tracking numbers from a hypothetical orders database.
    """
    return [os.environ.get("TRACKING_NUMBER", "6063488191737")]

def extract_korean(text):
    """Extracts Korean, numbers, dates, and some special characters, and removes trailing spaces."""
    return "".join(re.findall(r"[가-힣0-9:\s\.\(\)\-]+", text)).rstrip()

def crawl_delivery_status(trans_number):
    """Crawls delivery status and stores the result in the database."""
    url = f"https://acieshop.com/pod.php?OrderNo={trans_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    print(f"--- 운송장번호 {trans_number} 크롤링 시작 ---", flush=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            if not tables:
                print("❌ 테이블을 찾을 수 없습니다.")
                return False
            delivery_table = tables[-1]
            rows = delivery_table.find_all("tr")
            
            last_status_row = None
            recipient_info_row = None
            for row in reversed(rows):
                if row.find('td', {'colspan': '5'}):
                    recipient_info_row = row
                elif row.get_text(strip=True) and not last_status_row:
                    last_status_row = row
            
            if last_status_row:
                cells = last_status_row.find_all("td")
                final_status = ", ".join(extract_korean(cell.get_text()) for cell in cells)
                recipient_info = extract_korean(recipient_info_row.get_text()) if recipient_info_row else ""
                
                conn = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    password=DB_PASSWORD,
                    database=DB_NAME
                )
                cursor = conn.cursor()
                print(TABLE_NAME)
                try:
                    query = """
                    INSERT INTO delivery (tracking_number, status, recipient_info, crawled_at)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                     status=VALUES(status),
                     recipient_info=VALUES(recipient_info),
                     crawled_at=VALUES(crawled_at)
                    """
                    cursor.execute(query, (trans_number, final_status, recipient_info, datetime.now()))
                    
                    print(f"✅ 운송장번호 {trans_number}의 상태가 성공적으로 저장/업데이트되었습니다.", flush=True)
                except mysql.connector.Error as e:
                    print(f"데이터베이스 오류: {e}", flush=True)
                    return False
                finally:
                    conn.commit()
                    cursor.close()
                    conn.close()
                return True
            else:
                print("❌ 배달완료 상태를 찾을 수 없습니다.", flush=True)
                return False
        else:
            print(f"Failed to retrieve page: {response.status_code}", flush=True)
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {e}", flush=True)
        return False
    except mysql.connector.Error as e:
        print(f"MariaDB 연결 오류: {e}", flush=True)
        return False
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}", flush=True)
        return False
    finally:
        print(f"--- 운송장번호 {trans_number} 크롤링 종료 ---", flush=True)

def scheduled_crawl_job():
    """Job to be executed by the scheduler."""
    print(f"\n--- 스케줄링된 크롤링 작업 시작: {time.strftime('%Y-%m-%d %H:%M:%S')} ---", flush=True)
    tracking_numbers = get_tracking_numbers_for_period()
    if not tracking_numbers:
        print("확인할 운송장번호가 없습니다.", flush=True)
        return
    
    for number in tracking_numbers:
        crawl_delivery_status(number)
    
    print(f"--- 스케줄링된 크롤링 작업 종료: {time.strftime('%Y-%m-%d %H:%M:%S')} ---", flush=True)
