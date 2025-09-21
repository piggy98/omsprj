import requests

# 세션 객체 생성
session = requests.Session()

# 1. 로그인
login_url = "https://updream.shop/login.php"
login_data = {
    "user_id": "PAPA-ONE",       # 로그인 ID
    "user_pw": "비밀번호1234",   # 로그인 비밀번호
}
res = session.post(login_url, data=login_data)
print("로그인 결과:", res.status_code)

# 로그인 성공 여부 확인 (예: 메인 페이지 안에 사용자명 있는지 검사)
if "PAPA-ONE" not in res.text:
    print("❌ 로그인 실패 - ID/비번 확인 필요")
    exit()

# 2. 주문별 트래킹번호 등록
order_url = "https://updream.shop/dlvservice/order/order_detail_m.php"

data = {
    "actWork": "OrderALL",
    "Nno": "202509180733370003CXJ15",
    "UserID": "PAPA-ONE",
    "Station": "503",
    "OrderNo": "2025091724209851",
    "HawbNo": "6063488195566",
    "CneeName": "정다교",
    "CustomsNo": "P862151641135",
    "CneeTel": "010-8237-7813",
    "CneeHP": "010-8237-7813",
    "CneeZIP": "22800",
    "CneeAddr1": "인천광역시 서구 서달로123번길 12-4 (석남동, 신동아아파트) 1811호",
    "CneeAddr2": "",
    "MallType": "A",
    "GetBY": "1",
    "TrkNo": "1234567890",   # ✅ 실제 등록할 송장번호
}

res = session.post(order_url, data=data)
print("등록 결과:", res.status_code)
print(res.text[:500])  # 응답 일부만 출력
