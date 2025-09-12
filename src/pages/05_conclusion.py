import streamlit as st
import os
import base64
import re

# --- 페이지 기본 설정 ---
# 💡 'fullscreen' 레이아웃을 사용하여 좌우 여백을 최소화하고 HTML 콘텐츠에 집중
st.set_page_config(page_title="종합 분석 보고서", page_icon="📝", layout="wide")

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

# 💡 HTML 파일 경로
html_file_path = 'insight.html'

# 이미지를 Base64로 인코딩하는 함수
def get_image_as_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_string = f.read()

    # HTML 내의 모든 이미지 경로를 찾아 Base64로 인코딩된 데이터로 교체
    # 정규 표현식을 사용하여 src="report_images/..." 패턴을 찾음
    img_tags = re.findall(r'<img src="(report_images/[^"]+)"', html_string)

    for img_path in img_tags:
        base64_image = get_image_as_base64(img_path)
        if base64_image:
            # 데이터 URI 생성
            data_uri = f"data:image/png;base64,{base64_image}"
            # 원본 경로를 데이터 URI로 교체
            html_string = html_string.replace(img_path, data_uri)

    st.components.v1.html(html_string, height=3000, scrolling=True)

except FileNotFoundError:
    st.error(f"🚨 보고서 파일({html_file_path})을 찾을 수 없습니다.")
    st.info("프로젝트의 루트 디렉토리에 'insight.html' 파일이 있는지 확인해주세요.")