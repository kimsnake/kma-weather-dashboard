# utils/weather_emojis.py
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
    
    idx = val % 16
    return arr[idx], arrows[idx]

# [헬퍼 함수] 강수 형태 텍스트 정제
def clean_pty(pty_str):
    if not pty_str or pty_str == "-":
        return "없음"
    import re
    cleaned = re.sub(r'\s*\([0-9]+\)', '', str(pty_str))
    return cleaned

# [헬퍼 함수] SKY(하늘상태)와 PTY(강수형태) 기반 대표 이모지 산출
def get_representative_emoji(sky_val, pty_val):
    pty_str = str(pty_val).strip()
    sky_str = str(sky_val).strip()
    
    if pty_str in ["1", "비"]:
        return "🌧️"
    elif pty_str in ["2", "비/눈", "진눈개비"]:
        return "🌨️"
    elif pty_str in ["3", "눈"]:
        return "❄️"
    elif pty_str in ["4", "소나기"]:
        return "🌦️"
    
    current_hour = datetime.now(KST).hour
    is_daytime = 6 <= current_hour < 18
    
    if sky_str in ["1", "맑음"]:
        return "☀️" if is_daytime else "🌙"
    elif sky_str in ["3", "구름많음"]:
        return "⛅"
    elif sky_str in ["4", "흐림"]:
        return "☁️"
    else:
        return "☀️" if is_daytime else "🌙"

# [헬퍼 함수] 1시간 강수량 양에 따른 이모지 부여
def get_rainfall_emoji(rn1):
    try:
        val = float(rn1)
    except (TypeError, ValueError):
        return "➖"
    
    if val <= 0:
        return "➖"
    elif val < 3:
        return "🌦️"
    elif val < 10:
        return "🌧️"
    elif val < 30:
        return "☔"
    else:
        return "⛈️"

# [헬퍼 함수] 기온 체감 이모지 구성
def get_temperature_display(temp):
    try:
        val = float(temp)
    except (TypeError, ValueError):
        return f"{temp} ℃"
    
    if val >= 28:
        return f"🥵 {val} ℃"
    elif val >= 20:
        return f"😎 {val} ℃"
    elif val >= 10:
        return f"🧥 {val} ℃"
    elif val >= 0:
        return f"🥶 {val} ℃"
    else:
        return f"🧊 {val} ℃"

# [헬퍼 함수] 습도 사람 표정 이모지 구성 (습함 😡, 적당 😊, 건조 🥴)
def get_humidity_display(hum):
    try:
        val = float(hum)
    except (TypeError, ValueError):
        return f"{hum} %"
    
    if val >= 70:
        return f"😡 {val} %"
    elif val >= 40:
        return f"😊 {val} %"
    else:
        return f"🥴 {val} %"

# [헬퍼 함수] 강수 확률에 따른 파란색 배경 농도 및 스타일 반환
def get_pop_style(pop_val):
    try:
        val = int(float(pop_val))
    except (TypeError, ValueError):
        return "#f8f9fa", "#333333", "0%"
    
    if val >= 80:
        bg_color = "rgba(0, 123, 255, 0.35)"
        text_color = "#002752"
    elif val >= 50:
        bg_color = "rgba(0, 123, 255, 0.20)"
        text_color = "#004085"
    elif val >= 20:
        bg_color = "rgba(0, 123, 255, 0.08)"
        text_color = "#155724"
    else:
        bg_color = "#f8f9fa"
        text_color = "#495057"
        
    return bg_color, text_color, f"{val}%"