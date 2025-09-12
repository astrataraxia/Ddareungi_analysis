import streamlit as st
import os

# --- 페이지 기본 설정 ---
# 💡 'fullscreen' 레이아웃을 사용하여 좌우 여백을 최소화하고 HTML 콘텐츠에 집중
st.set_page_config(page_title="종합 분석 보고서", page_icon="📝", layout="wide" )

st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# --- HTML 파일 로드 및 표시 ---
st.title("📊 서울시 공공자전거 '따릉이' 데이터 분석 보고서")

# 💡 HTML 파일 경로
html_file_path = 'insight.html'

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_string = f.read()
    
    st.components.v1.html(html_string, height=3000, scrolling=True)

except FileNotFoundError:
    st.error(f"🚨 보고서 파일({html_file_path})을 찾을 수 없습니다.")
    st.info("프로젝트의 루트 디렉토리에 'insight.html' 파일이 있는지 확인해주세요.")