import os
import io
import requests
import pandas as pd
import streamlit as st

# 설정 정보 (GitHub 스토리지 레포 정보)
GITHUB_OWNER = "kimsnake"         # 본인 GitHub 아이디
STORAGE_REPO = "kma-weather-storage" # 스토리지 레포 이름
BRANCH = "main"

def _get_github_headers():
    """GitHub Private 레포 접근을 위한 인증 헤더 생성"""
    # STORAGE_KEY 또는 GITHUB_TOKEN 환경 변수 / Streamlit Secrets 지원
    token = (
        os.getenv("STORAGE_KEY") or 
        os.getenv("GITHUB_TOKEN") or 
        st.secrets.get("STORAGE_KEY", "") or 
        st.secrets.get("GITHUB_TOKEN", "")
    )
    headers = {
        "Accept": "application/vnd.github.v3+raw"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def _get_github_api_headers():
    """GitHub API 요청용 헤더 생성"""
    token = (
        os.getenv("STORAGE_KEY") or 
        os.getenv("GITHUB_TOKEN") or 
        st.secrets.get("STORAGE_KEY", "") or 
        st.secrets.get("GITHUB_TOKEN", "")
    )
    headers = {
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

@st.cache_data(ttl=600)
def load_collection_history():
    """GitHub 스토리지 레포에서 collection_history.csv 파일을 직접 읽어옵니다."""
    url = f"https://raw.githubusercontent.com/{GITHUB_OWNER}/{STORAGE_REPO}/{BRANCH}/meta_logs/collection_history.csv"
    headers = _get_github_headers()
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            df = pd.read_csv(io.BytesIO(response.content))
            return df
        else:
            st.error(f"로그 파일을 불러오지 못했습니다. (상태 코드: {response.status_code}) 토큰 권한을 확인해주세요.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"로그 파일 로드 중 오류 발생: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=600)
def load_latest_weather_file(region_prefix: str, data_type: str):
    """
    latest_weather_data 폴더에서 특정 지역과 타입(current_latest 또는 forecast_latest)에 맞는 CSV 파일을 읽어옵니다.
    - region_prefix: 예) "성남_55_127", "서울_대치동_61_126"
    - data_type: "current" 또는 "forecast"
    """
    api_url = f"https://api.github.com/repos/{GITHUB_OWNER}/{STORAGE_REPO}/contents/latest_weather_data"
    headers = _get_github_api_headers()
    
    try:
        res = requests.get(api_url, headers=headers)
        if res.status_code != 200:
            return pd.DataFrame()
            
        files_info = res.json()
        if not isinstance(files_info, list):
            return pd.DataFrame()
            
        target_keyword = f"{region_prefix}_{data_type}_latest.csv"
        
        for file_info in files_info:
            name = file_info.get("name", "")
            if target_keyword in name:
                download_url = file_info.get("download_url")
                if download_url:
                    file_res = requests.get(download_url, headers=_get_github_headers())
                    if file_res.status_code == 200:
                        return pd.read_csv(io.BytesIO(file_res.content))
                        
        return pd.DataFrame()
        
    except Exception as e:
        st.error(f"최신 날씨 데이터 로드 중 오류 발생: {e}")
        return pd.DataFrame()