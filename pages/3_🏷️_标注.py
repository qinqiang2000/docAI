import os
from PIL import Image
import streamlit as st
import pandas as pd
from streamlit_js_eval import streamlit_js_eval

from core.common import DATASET_DIR
from file_server import port
from tools.utitls import wide_styles, display_image, separator

st.set_page_config(
    page_title="标注",
    page_icon="🏷️",
    layout="wide",
    menu_items={
        'About': "#💡 This is a header. This is an *extremely* cool app!"
    }
)

# 读取数据集
df = pd.read_csv(os.path.join(DATASET_DIR, "dataset.csv"))

# 获取数据集名称
dataset_names = df['name'].tolist()

screen_height = streamlit_js_eval(js_expressions='screen.height', key='SCR')
height = None if not screen_height else screen_height - 100
hostname = streamlit_js_eval(js_expressions='window.location.hostname', key='hostname')

wide_styles()

def display_pdf(file_path):
    # 获取file_path的文件名字
    filename = file_path.split("/")[-1]
    pdf_url = f"http://{hostname}:{port}/files?fn={DATASET_DIR}/{st.session_state['dataset_id']}/{filename}"
    pdf_display = f'<embed src="{pdf_url}" type="application/pdf" width="100%" height={height} />'
    st.markdown(pdf_display, unsafe_allow_html=True)


# 在侧边栏中创建第一个selectbox
with st.sidebar:
    selected_dataset = st.selectbox('数据集', dataset_names)

    # 获取选中的数据集的文件列表
    if selected_dataset:
        row = df[df['name'] == selected_dataset]
        # row取id一列的值
        st.session_state['dataset_id'] = row['id'].values[0]
        selected_files = row['files'].values[0].split(separator)
        selected_files = [file.strip() for file in selected_files]
        st.session_state['selected_file'] = st.selectbox('文件列表', selected_files)

# 在主区域创建两列布局
col1, col2 = st.columns([0.65, 0.35])

# 在左列显示选中的文件
with col1.container():
    if 'selected_file'in st.session_state and st.session_state['selected_file']:
        selected_file = st.session_state['selected_file']
        file_path = os.path.join(DATASET_DIR, st.session_state['dataset_id'], selected_file)
        if os.path.exists(file_path):
            # 判断文件类型，如果是图片则使用PIL库打开并显示
            if file_path.lower().endswith('.pdf'):
                display_pdf(file_path)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                display_image(file_path)
        else:
            col1.warning(f"文件 {selected_file} 不存在")