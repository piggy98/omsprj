import re
import requests
import os
import time
import signal
import sys
from bs4 import BeautifulSoup
# from apscheduler.schedulers.background import BackgroundScheduler

def extract_korean(text):
    """한글, 숫자, 날짜, 특수기호 일부를 포함하고 오른쪽 공백을 제거합니다."""
    return "".join(re.findall(r"[가-힣0-9:\s\.\(\)\-]+", text)).rstrip()

def crawl_delivery_status():
    """배송 상태를 크롤링하고 결과를 표준 출력으로 보냅니다."""
    # 배달 완료된 운송장 번호(기본값)와 배달이 완료되지 않은 운송장 번호를 모두 테스트할 수 있도록 변경했습니다.
    # HTML 소스에 따라 '6063488190901'은 배달 완료, '6063488191737'은 배달 진행 중입니다.
    trans_number = os.environ.get("TRACKING_NUMBER", "6063488190901")
    url = f"https://acieshop.com/pod.php?OrderNo={trans_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    print(f"\n--- 크롤링 작업 시작: {time.strftime('%Y-%m-%d %H:%M:%S')} ---", flush=True)
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            tables = soup.find_all("table")

            if not tables:
                print("❌ 테이블을 찾을 수 없습니다.")
                return

            # 배송 현황 테이블은 보통 마지막에 위치합니다.
            delivery_table = tables[-1]
            rows = delivery_table.find_all("tr")

            # 마지막 상태를 찾기 위해 rows 리스트를 역순으로 순회합니다.
            last_status_row = None
            recipient_info_row = None
            
            for row in reversed(rows):
                # 수령인 정보 행(colspan="5")을 먼저 찾습니다.
                if row.find('td', {'colspan': '5'}):
                    recipient_info_row = row
                # 상태 정보 행(내용이 비어있지 않은 첫 번째 행)을 찾습니다.
                elif row.get_text(strip=True) and not last_status_row:
                    last_status_row = row
            
            # 최종 상태 정보 추출
            if last_status_row:
                cells = last_status_row.find_all("td")
                final_status = ", ".join(extract_korean(cell.get_text()) for cell in cells)
                
                # 수령인 정보 추출
                recipient_info = ""
                if recipient_info_row:
                    recipient_info = extract_korean(recipient_info_row.get_text())
                
                delivery_message = f"""📦 운송장번호: {trans_number}
{final_status}
{recipient_info if recipient_info else ""}
"""
                print(delivery_message, flush=True)
            else:
                print("❌ 배송 현황을 찾을 수 없습니다.")

        else:
            print(f"Failed to retrieve page: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"요청 실패: {e}")
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
    print(f"--- 크롤링 작업 종료: {time.strftime('%Y-%m-%d %H:%M:%S')} ---", flush=True)

def signal_handler(signum, frame):
    """컨테이너 종료 신호를 처리하는 핸들러."""
    print(f"종료 신호({signum})를 받았습니다. 스케줄러를 종료합니다.")
    sys.exit(0)

# def main():
#     """스케줄러를 초기화하고 실행하는 메인 함수입니다."""
    
#     # SIGTERM 신호 핸들러 등록
#     signal.signal(signal.SIGTERM, signal_handler)

#     scheduler = BackgroundScheduler()
#     # 30초마다 crawl_delivery_status 함수 실행
#     scheduler.add_job(crawl_delivery_status, 'interval', minutes=0.5)
    
#     print("스케줄러 시작. 30초마다 배송 상태를 확인합니다.")
#     scheduler.start()

#     try:
#         # 메인 스레드가 종료되지 않도록 유지
#         while True:
#             time.sleep(1)
#     except (KeyboardInterrupt, SystemExit):
#         # Ctrl+C 또는 기타 종료 신호 시 스케줄러를 안전하게 종료
#         print("스케줄러 종료 중...")
#         scheduler.shutdown()
#         print("스케줄러가 종료되었습니다.")

if __name__ == "__main__":
    crawl_delivery_status()
