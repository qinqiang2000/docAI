import json
import os

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from streamlit import session_state as session
from tools.utitls import custom_page_styles

st.set_page_config(
    page_title="Preview",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认隐藏侧边栏
)

# 自定义CSS来减少边距和填充
custom_page_styles(0)

screen_height = streamlit_js_eval(js_expressions='screen.height', key='SCR')
height = None if not screen_height else screen_height - 90
hostname = streamlit_js_eval(js_expressions='window.location.hostname', key='hostname')

port = 8090


def display_pdf(file_path):
    # 获取file_path的文件名字
    filename = file_path.split("/")[-1]
    pdf_url = f"http://{hostname}:{port}/files?fn=tmp/{filename}"
    pdf_display = f'<embed src="{pdf_url}" type="application/pdf" width="100%" height={height} />'
    st.markdown(pdf_display, unsafe_allow_html=True)


def load_data(_id):
    json_file = f"tmp/{_id}.json"
    if os.path.exists(json_file):
        with open(json_file, 'r') as file:
            return json.load(file)
    return None


cols = [0.65, 0.35]
col1, col2 = st.columns(cols)

fn = None
_id = None
if 'fn' in st.query_params:
    fn = st.query_params['fn']
    _id = fn.split(".")[0]

# 左面板，预览PDF或图片
with col1.container():
    if fn:
        display_pdf(fn)

with col2.container(height=height, border=False):  # Adjusted for interface elements
    _json = load_data(_id)
    print(f"_id: {_id}, json: {_json} ")
    if _json:
        st.write(_json)

