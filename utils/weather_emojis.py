from datetime import datetime
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

# [헬퍼 함수] 풍향 각도를 받아 화살표와 한글 방위로 변환하는 함수
def deg_to_compass(deg):
    try:
        deg = float(deg)
    except (TypeError, ValueError):
        return "-", "❓"
    val = int((deg / 22.5) + 0.5)
    arr = ["북", "북북동", "동북동", "동북동", "동", "동남동", "동남동", "남남동", "남", "남남서", "서남서", "서남서", "서", "서북서", "북서", "북북서"]
    arrows = ["⬇️", "↙️", "⬅️", "↖️", "⬆️", "↗️", "➡️", "↘️", "⬇️", "↙️", "⬅️", "↖️", "⬆️", "↗️", "➡️", "↘️"]
    return arr[val % 16], arrows[val % 16]

# [헬퍼 함수] 강수 형태 텍스트 정제
def clean_pty(pty_str):
    if not pty_str or pty_str == "-":
        return "없음"
    import re
    return re.sub(r'\s*\([0-9]+\)', '', str(pty_str))

# [헬퍼 함수] 하늘상태(SKY) 이모지 단독 산출 (구름많음(3), 흐림(4) 등 괄호 텍스트 완벽 대응)
def get_sky_emoji(sky_val, target_hour=None):
    sky_str = str(sky_val).strip()
    
    if target_hour is None:
        target_hour = datetime.now(KST).hour
        
    # 새벽 5시는 밤(🌙)으로 처리 (06:00부터 낮)
    is_daytime = 6 <= target_hour < 18
    
    if "1" in sky_str or "맑음" in sky_str:
        return "☀️" if is_daytime else "🌙"
    elif "3" in sky_str or "구름많음" in sky_str:
        return "⛅"
    elif "4" in sky_str or "흐림" in sky_str:
        return "☁️"
    else:
        return ""

# [헬퍼 함수] 강수형태(PTY) 이모지 단독 산출 ('없음(0)' 등 완벽 차단)
def get_pty_emoji(pty_val):
    pty_str = str(pty_val).strip()
    
    if not pty_str or "없음" in pty_str or "0" in pty_str or pty_str in ["-", "none", "None"]:
        return ""
        
    if "비" in pty_str or "1" in pty_str:
        return "🌧️"
    elif "진눈개비" in pty_str or "2" in pty_str:
        return "🌨️"
    elif "눈" in pty_str or "3" in pty_str:
        return "❄️"
    elif "소나기" in pty_str or "4" in pty_str:
        return "🌦️"
        
    return ""

# [하위 호환용 조합 함수]
def get_representative_emoji(sky_val, pty_val, forecast_time=None):
    target_hour = None
    if forecast_time:
        try:
            time_str = str(forecast_time).strip()
            if " " in time_str:
                time_str = time_str.split(" ")[1]
            if ":" in time_str:
                target_hour = int(time_str.split(":")[0])
        except (ValueError, TypeError):
            pass
            
    sky_emoji = get_sky_emoji(sky_val, target_hour)
    pty_emoji = get_pty_emoji(pty_val)
    return f"{sky_emoji}{pty_emoji}" if pty_emoji else sky_emoji

# [헬퍼 함수] 1시간 강수량 양에 따른 이모지 부여
def get_rainfall_emoji(rn1):
    try:
        val = float(rn1)
    except (TypeError, ValueError):
        return "➖"
    if val <= 0: return "➖"
    elif val < 3: return "🌦️"
    elif val < 10: return "🌧️"
    elif val < 30: return "☔"
    else: return "⛈️"

# [헬퍼 함수] 기온 체감 이모지 구성
def get_temperature_display(temp):
    try: val = float(temp)
    except: return f"{temp} ℃"
    if val >= 28: return f"🥵 {val} ℃"
    elif val >= 20: return f"😎 {val} ℃"
    elif val >= 10: return f"🧥 {val} ℃"
    elif val >= 0: return f"🥶 {val} ℃"
    else: return f"🧊 {val} ℃"

# [헬퍼 함수] 습도 사람 표정 이모지 구성
def get_humidity_display(hum):
    try: val = float(hum)
    except: return f"{hum} %"
    if val >= 70: return f"😡 {val} %"
    elif val >= 40: return f"😊 {val} %"
    else: return f"🥴 {val} %"

# [헬퍼 함수] 강수 확률에 따른 파란색 배경 농도 및 스타일 반환
def get_pop_style(pop_val):
    try: val = int(float(pop_val))
    except: return "#f8f9fa", "#333333", "0%"
    if val >= 80: return "rgba(0, 123, 255, 0.35)", "#002752", f"{val}%"
    elif val >= 50: return "rgba(0, 123, 255, 0.20)", "#004085", f"{val}%"
    elif val >= 20: return "rgba(0, 123, 255, 0.08)", "#155724", f"{val}%"
    else: return "#f8f9fa", "#495057", f"{val}%"