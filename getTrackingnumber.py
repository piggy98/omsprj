from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# 크롬 드라이버 실행 (로그인 세션 유지하려면 user-data-dir 지정)
options = webdriver.ChromeOptions()
options.add_argument("user-data-dir=C:/Users/사용자명/AppData/Local/Google/Chrome/User Data")  # 크롬 프로필 경로
driver = webdriver.Chrome(options=options)

url = "https://www.amazon.com/gp/your-account/ship-track?itemId=jjqptopqoqopqmp&orderId=113-5976458-0723440&shipmentId=DkYnjwVbM&packageIndex=0&ref_=ppx_hzod_shipconns_dt_b_track_package_0"
driver.get(url)

time.sleep(5)  # 페이지 로딩 대기

# 트래킹 번호 추출
tracking_element = driver.find_element(By.CSS_SELECTOR, "#pt-page-container-inner > div.a-row.pt-main-container > div.pt-map-outer-container.pt-map-type-static > div.pt-floating-map-card > section > div.pt-delivery-card-wrapper > div:nth-child(1) > div")
print("Tracking Number:", tracking_element.text)

driver.quit()
