import pprint

import pyupbit
import time
import datetime

# 비트업 인증 객체생성
f = open("220215_key.txt")
lines = f.readlines()
access_key = lines[0].strip()
secret_key = lines[1].strip()
gubun = lines[2].strip()
cash_per = float(lines[3].strip())
k_data = float(lines[4].strip())
ticker_nm = lines[5].strip()
f.close()

upbit = pyupbit.Upbit(access_key, secret_key)  # class instance, object

# 변수 설정
# ticker_nm = "KRW-WAVES"
# cash_per = 0.3
# k_data = 0.5
op_mode = False # 프로그램 당일에는 매수 안도록 하기 위해.
hold = False    # 매수 유/무 판단.

# 목표가 구하기 - 래리 윌리엄스
def cal_target(ticker):
    df = pyupbit.get_ohlcv(ticker, "day")
    yesterday = df.iloc[-2]
    today = df.iloc[-1]
    yesterday_range = yesterday['high']-yesterday['low']
    target = today['open'] + (yesterday_range * k_data)
    return target

def get_yesterday_ma5(ticker) :
    df = pyupbit.get_ohlcv(ticker)
    close = df['close']
    ma = close.rolling(5).mean()
    return ma[-1]

if gubun == "1" :
    op_mode = True
    hold = True


target_pri  = cal_target(ticker_nm)
ma5 = get_yesterday_ma5(ticker_nm)

# 1초에 한번씩 현재가 가져오기
while True :
    price = pyupbit.get_current_price(ticker_nm)
    now = datetime.datetime.now()

    # 09시 목표가 갱신
    # if (now.hour == 16) and (now.minute == 38) and (20 <= now.second <= 30):
    if (now.hour == 9) and (now.minute == 00) and (20 <= now.second <= 30):
        target_pri = cal_target(ticker_nm)
        time.sleep(10)
        op_mode = True

    # 매수시도. 매초마다 조건을 확인한 후 매수 시도.
    if (op_mode is True) and (price is not None) and (price >= target_pri) and (hold is False):
        ma5 = get_yesterday_ma5(ticker_nm)
        if (price >= ma5) :
            krw_balance = upbit.get_balance("KRW")
            upbit.buy_market_order(ticker_nm,krw_balance * cash_per)  # 시장가 체결
            hold = True

    # 매도 시도.
    # if (now.hour == 18 ) and (now.minute == 00) and (50 <= now.second <= 59):
    if (now.hour == 8) and (now.minute == 55) and (50 <= now.second <= 59):
        if op_mode is True and hold is True :
            btc_balance = upbit.get_balance(ticker_nm)
            upbit.sell_market_order(ticker_nm,btc_balance)
            hold = False
        op_mode = False # 새로운 거래일에서 목표가 갱신될때까지 거래가 되지 않도록
        time.sleep(10)

    # print(now,price," : ",target_pri )
    # print(upbit.get_balance(ticker_nm)*0.1)
    # 상태출력 up
    print(f"현재시간: {now} 목표가: {target_pri} 현재가: {price} MA5: {ma5} 보유상태: {hold} 동작상태:{op_mode}")

    time.sleep(2)



# # 자산정보
# upbit = pyupbit.Upbit(access_key, secret_key)  # class instance, object
# balance = upbit.get_balance("KRW-BTC")
# print(balance, type(balance))
#
# balances = upbit.get_balances()
# pprint.pprint(balances)
# print(balances[6])