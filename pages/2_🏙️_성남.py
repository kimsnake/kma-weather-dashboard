import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
from utils.data_loader import load_latest_weather_file
from utils.weather_emojis import (
    deg_to_compass,
    clean_pty,
    get_sky_emoji,
    get_pty_emoji,
    get_rainfall_emoji,
    get_temperature_display,
    get_humidity_display,
    get_pop_style
)

# 페이지 설정
st.set_page_config(page_title="성남 날씨 대시보드", page_icon="🏙️", layout="wide")

# 한국 시간 타임존
KST = ZoneInfo("Asia/Seoul")

# [자동 새로고침 설정] 30초(30000ms)마다 백그라운드 체크
count = st_autorefresh(interval=30 * 1000, key="weather_autorefresh")

current_time = datetime.now(KST)
if current_time.minute == 50:
    st.cache_data.clear()

# UI 컴포넌트 스타일링 커스텀
st.markdown("""
    <style>
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🏙️ 성남시 날씨 대시보드")
st.markdown("기상청 API를 통해 수집된 성남(`55_127`) 지역의 실시간 및 예보 데이터입니다.")
st.markdown("---")

REGION_KEY = "성남_55_127"

with st.spinner("성남 데이터를 불러오는 중..."):
    df_current = load_latest_weather_file(REGION_KEY, "current")
    df_forecast = load_latest_weather_file(REGION_KEY, "forecast")

# 1. 현재 날씨 섹션
st.subheader("🌡️ 성남 날씨 현황")

if not df_current.empty:
    curr_row = df_current.iloc[-1]
    
    collect_time = str(curr_row.get("수집시각", "정보 없음"))
    
    base_date_raw = None
    base_time_raw = None
    
    for col in curr_row.index:
        col_clean = str(col).strip()
        if "발표일자" in col_clean or col_clean == "발표일자":
            base_date_raw = curr_row[col]
        elif "발표시각" in col_clean or col_clean == "발표시각":
            base_time_raw = curr_row[col]
            
    if base_date_raw is None and len(curr_row.index) > 1:
        base_date_raw = curr_row.iloc[1]
    if base_time_raw is None and len(curr_row.index) > 2:
        base_time_raw = curr_row.iloc[2]

    base_date = str(base_date_raw).split('.')[0].strip() if base_date_raw is not None and pd.notna(base_date_raw) else ""
    
    if base_time_raw is not None and pd.notna(base_time_raw):
        try:
            base_time = str(int(float(base_time_raw))).zfill(4)
        except (ValueError, TypeError):
            base_time = str(base_time_raw).split('.')[0].strip().zfill(4)
    else:
        base_time = "0000"
        
    if len(base_date) == 8 and len(base_time) >= 4:
        base_formatted = f"{base_date[:4]}-{base_date[4:6]}-{base_date[6:]} {base_time[:2]}:{base_time[2:4]}"
    else:
        base_formatted = f"{base_date} {base_time}" if base_date else "정보 없음"
    
    temp_raw = curr_row.get("기온(℃)[T1H]", "-")
    hum_raw = curr_row.get("습도(%)[REH]", "-")
    pty_raw = curr_row.get("강수형태[PTY]", "0")
    sky_current_raw = curr_row.get("하늘상태[SKY]", "1")
    rn1_raw = curr_row.get("1시간강수량[RN1]", "-")
    wsd = curr_row.get("풍속(m/s)[WSD]", "-")
    vec = curr_row.get("풍향(deg)[VEC]", "-")

    temp_text = get_temperature_display(temp_raw)
    hum_text = get_humidity_display(hum_raw)
    pty_clean = clean_pty(pty_raw)
    
    rn1_emoji = get_rainfall_emoji(rn1_raw)
    compass_text, arrow_icon = deg_to_compass(vec)

    st.markdown(f"<p style='color: #666; font-size: 14px; margin-bottom: 10px;'>⏱️ <b>수집 시각:</b> {collect_time} &nbsp;|&nbsp; 📡 <b>기상청 발표 시각:</b> {base_formatted}</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="현재 기온", value=temp_text)
    with col2:
        st.metric(label="습도", value=hum_text)
    with col3:
        # 💡 강수 형태 칸에는 이모지를 빼고 깔끔하게 텍스트(없음, 비 등)만 출력
        st.metric(label="강수 형태", value=pty_clean)

    st.markdown("<div style='margin: 10px 0;'></div>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.metric(label="1시간 강수량", value=f"{rn1_emoji} {rn1_raw} mm" if rn1_raw != "-" else "-")
    with col5:
        st.metric(label="풍속", value=f"💨 {wsd} m/s" if wsd != "-" else "-")
    with col6:
        st.metric(label="풍향", value=f"{arrow_icon} {compass_text}", delta=f"{vec}°" if vec != "-" else None)
else:
    st.warning("성남 현재 날씨 데이터를 찾을 수 없습니다.")

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# 2. 단기 예보 섹션
st.subheader("📅 성남 단기 예보 트렌드")

if not df_forecast.empty:
    latest_row = df_forecast.iloc[-1]
    
    forecast_items = []
    for i in range(1, 7):
        prefix = f"+{i}_"
        time_col = f"{prefix}예보시각"
        if time_col in latest_row and pd.notna(latest_row[time_col]):
            temp_val = latest_row.get(f"{prefix}기온(℃)[T1H]")
            hum_val = latest_row.get(f"{prefix}습도(%)[REH]")
            sky_val = latest_row.get(f"{prefix}하늘상태[SKY]")
            pty_val = latest_row.get(f"{prefix}강수형태[PTY]")
            
            forecast_items.append({
                "time": latest_row.get(time_col),
                "temp": f"{temp_val} ℃" if temp_val != "-" else "-",
                "hum": f"{hum_val} %" if hum_val != "-" else "-",
                "pop": latest_row.get(f"{prefix}강수확률(%)[POP]"),
                "sky": sky_val,
                "pty": pty_val
            })
            
    if forecast_items:
        cols = st.columns(len(forecast_items))
        for idx, item in enumerate(forecast_items):
            with cols[idx]:
                bg_color, text_color, pop_str = get_pop_style(item["pop"])
                
                # 예보 시각(Hour) 안전 파싱
                target_hour = 12
                try:
                    time_part = str(item["time"]).strip()
                    if " " in time_part:
                        time_part = time_part.split(" ")[1]
                    if ":" in time_part:
                        target_hour = int(time_part.split(":")[0])
                except (ValueError, IndexError, TypeError):
                    target_hour = 12
                
                # 유틸 함수를 통해 예보 카드 이모지 산출 (하늘 상태 + 강수 형태 듀얼)
                sky_emoji = get_sky_emoji(item["sky"], target_hour)
                pty_emoji = get_pty_emoji(item["pty"])
                display_emoji = f"{sky_emoji}{pty_emoji}" if pty_emoji else sky_emoji
                
                st.markdown(f"""
                    <div style="background-color: {bg_color}; border: 1px solid #b8daff; padding: 12px; border-radius: 10px; text-align: center;">
                        <b style="font-size: 14px; color: #333;">{item['time']}</b><hr style="margin: 6px 0;">
                        <div style="font-size: 22px; margin: 4px 0;">{display_emoji}</div>
                        <div style="font-size: 15px; font-weight: bold; color: {text_color}; margin: 4px 0;">☂️ {pop_str}</div>
                        <div style="font-size: 12px; color: #333; margin-top: 6px;">
                            {item['temp']} &nbsp;|&nbsp; {item['hum']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("파싱 가능한 단기 예보 데이터가 없습니다.")
else:
    st.warning("성남 단기 예보 데이터를 찾을 수 없습니다.")

# [이모지 가이드 가이드라인 박스 추가]
st.markdown("<br>", unsafe_allow_html=True)
with st.container():
    st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef; font-size: 13px; color: #495057;">
            <b>📌 날씨 이모지 가이드</b><br><br>
            <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                <div><b>[하늘 상태]</b> ☀️ 맑음(낮) &nbsp;|&nbsp; 🌙 맑음(밤) &nbsp;|&nbsp; ⛅ 구름많음 &nbsp;|&nbsp; ☁️ 흐림</div>
                <div><b>[강수 형태]</b> 🌧️ 비 &nbsp;|&nbsp; 🌦️ 소나기 &nbsp;|&nbsp; 🌨️ 진눈개비 &nbsp;|&nbsp; ❄️ 눈</div>
                <div><b>[기타 지표]</b> ☂️ 강수확률 &nbsp;|&nbsp; 🥵~🧊 체감 기온 &nbsp;|&nbsp; 😡~🥴 습도 상태</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 3. 원본 데이터 모아보기 섹션
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.subheader("🔍 수집된 원본 데이터 모아보기")

with st.expander("📄 실시간 날씨 원본 데이터 (Current DF)", expanded=False):
    if not df_current.empty:
        st.dataframe(df_current, width="stretch", hide_index=True)
    else:
        st.info("실시간 데이터가 없습니다.")

with st.expander("📄 단기 예보 원본 데이터 (Forecast DF)", expanded=False):
    if not df_forecast.empty:
        st.dataframe(df_forecast, width="stretch", hide_index=True)
    else:
        st.info("예보 데이터가 없습니다.")