import streamlit as st
from utils.data_loader import load_collection_history

st.set_page_config(
    page_title="KMA Weather Dashboard",
    page_icon="⛅",
    layout="wide"
)

st.title("⛅ KMA Weather Monitoring Dashboard")
st.markdown("기상청 날씨 데이터 수집 현황 및 지역별 상세 대시보드입니다.")
st.info("👈 좌측 사이드바에서 메뉴나 지역(성남 등)을 선택해 주세요.")

st.divider()

# 전체 수집 로그 요약 살짝 보여주기
st.subheader("📊 최근 수집 히스토리 요약")
df_log = load_collection_history()
if not df_log.empty:
    st.dataframe(df_log.tail(5), use_container_width=True)
else:
    st.warning("수집 로그를 불러오지 못했거나 파일이 없습니다. GitHub 토큰(STORAGE_KEY) 설정을 확인해주세요.")