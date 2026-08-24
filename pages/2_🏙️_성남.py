import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from streamlit_autorefresh import st_autorefresh
from utils.data_loader import load_latest_weather_file
from utils.weather_emojis import (
    deg_to_compass,
    clean_pty,
    get_representative_emoji,
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
# 매 시간 50분이 되면 캐시를 비우고 데이터를 최신으로 갱신합니다.
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
    
    # [안전 파싱 및 강제 탐색] 컬럼명 매칭 실패 시 인덱스(iloc)로 안전하게 추출
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

    # 날짜 정제
    base_date = str(base_date_raw).split('.')[0].strip() if base_date_raw is not None and pd.notna(base_date_raw) else ""
    
    # 시간 정제 (숫자 0, 0.0, 문자열 0000 등 모든 포맷을 4자리 '0000'으로 안전 보정)
    if base_time_raw is not None and pd.notna(base_time_raw):
        try:
            base_time = str(int(float(base_time_raw))).zfill(4)
        except (ValueError, TypeError):
            base_time = str(base_time_raw).split('.')[0].strip().zfill(4)
    else:
        base_time = "0000"
        
    # 최종 발표 시각 포맷팅
    if len(base_date) == 8 and len(base_time) >= 4:
        base_formatted = f"{base_date[:4]}-{base_date[4:6]}-{base_date[6:]} {base_time[:2]}:{base_time[2:4]}"
    else:
        base_formatted = f"{base_date} {base_time}" if base_date else "정보 없음"
    
    temp_raw = curr_row.get("기온(℃)[T1H]", "-")
    hum_raw = curr_row.get("습도(%)[REH]", "-")
    pty_raw = curr_row.get("강수형태[PTY]", "0")
    rn1_raw = curr_row.get("1시간강수량[RN1]", "-")
    wsd = curr_row.get("풍속(m/s)[WSD]", "-")
    vec = curr_row.get("풍향(deg)[VEC]", "-")

    temp_text = get_temperature_display(temp_raw)
    hum_text = get_humidity_display(hum_raw)
    pty_clean = clean_pty(pty_raw)
    curr_rep_emoji = get_representative_emoji("1", pty_raw)
    rn1_emoji = get_rainfall_emoji(rn1_raw)
    compass_text, arrow_icon = deg_to_compass(vec)

    st.markdown(f"<p style='color: #666; font-size: 14px; margin-bottom: 10px;'>⏱️ <b>수집 시각:</b> {collect_time} &nbsp;|&nbsp; 📡 <b>기상청 발표 시각:</b> {base_formatted}</p>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="현재 기온", value=temp_text)
    with col2:
        st.metric(label="습도", value=hum_text)
    with col3:
        st.metric(label="강수 형태", value=f"{curr_rep_emoji} {pty_clean}")

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
            
            forecast_items.append({
                "time": latest_row.get(time_col),
                "temp": f"{temp_val} ℃" if temp_val != "-" else "-",
                "hum": f"{hum_val} %" if hum_val != "-" else "-",
                "pop": latest_row.get(f"{prefix}강수확률(%)[POP]"),
                "sky": latest_row.get(f"{prefix}하늘상태[SKY]"),
                "pty": latest_row.get(f"{prefix}강수형태[PTY]")
            })
            
    if forecast_items:
        cols = st.columns(len(forecast_items))
        for idx, item in enumerate(forecast_items):
            with cols[idx]:
                bg_color, text_color, pop_str = get_pop_style(item["pop"])
                rep_em = get_representative_emoji(item["sky"], item["pty"])
                
                st.markdown(f"""
                    <div style="background-color: {bg_color}; border: 1px solid #b8daff; padding: 12px; border-radius: 10px; text-align: center;">
                        <b style="font-size: 14px; color: #333;">{item['time']}</b><hr style="margin: 6px 0;">
                        <div style="font-size: 22px; margin: 4px 0;">{rep_em}</div>
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

# 3. 원본 데이터 모아보기 섹션 (페이지 맨 아래)
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