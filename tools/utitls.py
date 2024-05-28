import os

import streamlit as st
from PIL import Image
import pandas as pd
import fitz

separator = "|"


def get_page_count(file_path):
    # 获取文件的扩展名
    extension = os.path.splitext(file_path)[1].lower()

    if extension == '.pdf':
        # 如果文件是PDF，使用PyMuPDF获取页数
        with open(file_path, 'rb') as file:
            doc = fitz.open(file)
            page_count = len(doc)
        return page_count
    elif extension in ['.png', '.jpg', '.jpeg']:
        # 如果文件是图片，返回1
        return 1
    else:
        # 如果文件类型不支持，返回None
        return None


def display_image(file):
    image = Image.open(file)
    if 'rotated_image' not in st.session_state:
        st.session_state['rotated_image'] = image

    st.image(st.session_state['rotated_image'], use_column_width=True)

    _, col1, col2, _ = st.columns([3 / 8, 1 / 8, 1 / 8, 3 / 8])
    with col1:
        if st.button("↩️"):
            st.session_state['rotated_image'] = st.session_state['rotated_image'].rotate(90, expand=True)
            st.rerun()
    with col2:
        if st.button("↪️"):
            st.session_state['rotated_image'] = st.session_state['rotated_image'].rotate(-90, expand=True)
            st.rerun()


# 定制表格列style
def style_columns(df):
    def key_text_color(val):
        return 'color: black'

    def val_text_color(val):
        return 'color: #2b66c2'

    return (df.style
            .map(key_text_color, subset=['key'])  # Using .map for column-wise styling
            .map(val_text_color, subset=['value']))


def show_struct_data(name, data_list, edit=False, cc=None, styles=None, filename=None):
    """
    显示提取的结构化数据。
    参数:
    name (str): 提取器的名称。
    data_list (list): 包含提取的数据的列表，每个元素是一个字典，表示一页的数据。
    """
    if not cc:
        cc = {
            "key": st.column_config.TextColumn(
                "key", help="关键要素", width=None, disabled=True
            ),
            "value": st.column_config.TextColumn(
                "value", help="N/A: 表示任意值；不输入表示必须为空", width="large"
            ),
        }
    if not styles:
        styles = style_columns

    edited_data = []
    for i, page_data in enumerate(data_list):
        prefix = "" if name is None else f"[{name}]"
        prefix += "" if filename is None else f"{filename}"
        st.write(prefix, "第", i + 1, "页")
        for j, item in enumerate(page_data):
            df = pd.DataFrame(list(item.items()))
            df.columns = ['key', 'value']
            if not edit:
                st.dataframe(styles(df), hide_index=True, use_container_width=True, column_config=cc)
            else:
                d = st.data_editor(styles(df), hide_index=True, use_container_width=True, column_config=cc,
                                key=f"data_editor_{i}_{j}")
                edited_data.append(d)
    return edited_data


def custom_page_styles(padding_top=1, height=856):
    st.markdown(f"""
    <style>
    /* 用于整个页面的块容器的样式 */
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: {padding_top}rem;
        padding-right: 1rem; /* 右边距 */
        padding-left: 1rem; /* 左边距 */
        padding-bottom: 0rem;
    }}
    [data-testid="stDataFrame"]  {{
        white-space: pre-wrap; /* CSS property to make whitespace significant */
    }}    
    section.main>div {{
        padding-bottom: 1rem;
    }}
    [data-testid="column"]>div>div>div>div>div {{
        overflow: auto;
        height: {height}px;
    }}
    """, unsafe_allow_html=True)