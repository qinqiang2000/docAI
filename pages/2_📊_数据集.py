from datetime import datetime

import streamlit as st
import pandas as pd
import os
import uuid
import shutil

from core.common import DATASET_DIR
from core.extractor_manager import ExtractorManager  # Ensure the correct path
from tools.utitls import separator

st.set_page_config(
    page_title="数据集",
    page_icon="📊",
    menu_items={
        'About': "#💡 This is a header. This is an *extremely* cool app!"
    }
)
# Initialize the ExtractorManager
manager = ExtractorManager()

# Setup directories for saving files
if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)


def save_uploaded_files(id, uploaded_files):
    # Create a directory for the current dataset entry
    dataset_path = os.path.join(DATASET_DIR, id)
    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    saved_files = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(dataset_path, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        saved_files.append(uploaded_file.name)  # Only store the file name
    return separator.join(saved_files)


def save_data(df):
    st.session_state['data'] = df
    st.session_state['data'].to_csv(os.path.join(DATASET_DIR, "dataset.csv"), index=False)

    # Delete directories that are not in the dataset
    # Get the list of directories in DATA_DIR
    dir_list = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]

    # Get the list of ids from df
    id_list = df['id'].tolist()

    # Delete directories that are in dir_list but not in id_list
    for directory in dir_list:
        if directory not in id_list:
            shutil.rmtree(os.path.join(DATASET_DIR, directory))


def load_data():
    if 'data' not in st.session_state:
        st.session_state['data'] = pd.read_csv(os.path.join(DATASET_DIR, "dataset.csv"))
    return pd.DataFrame(columns=["id", "name", "extractor", "num", "files"])


load_data()
extractors = manager.get_extractors_list()

# --- 页面视图 ---
st.title("Dataset Management")

# File uploader
st.write("1.上传文件集:")
uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True, type=['pdf', 'jpg', 'jpeg', 'png'],
                                  label_visibility="collapsed")

c1, c2, _ = st.columns([1, 2, 17])
c1.write("2.")
add_button = c2.button("新增")
if add_button and uploaded_files:
    new_id = str(uuid.uuid4())[:5]
    files_str = save_uploaded_files(new_id, uploaded_files)
    new_row = pd.DataFrame([[new_id, "", "", len(files_str.split(separator)), files_str]],
                           columns=["id", "name", "extractor", "num", "files"])
    st.session_state.data = pd.concat([st.session_state.data, new_row], ignore_index=True)
elif add_button and not uploaded_files:
    st.error("Please upload files first!", icon='🚨')

st.write("3. 编辑名字&选择提取器:")
column_config = {
    "id": {"disabled": True},
    "name": st.column_config.TextColumn(
            help="填写数据集名称",
            max_chars=20,
            required=True,
        ),
    "extractor":
        st.column_config.SelectboxColumn(
            help="选择提取器",
            width="medium",
            options=extractors,
            required=True,
        ),
    "num": {"label": "No. of files", "disabled": True},
    "files": {"disabled": True},
}

# Display the data editor
ds = st.data_editor(data=st.session_state.data, column_config=column_config, hide_index=True, num_rows="dynamic",
                    column_order=("name", "extractor", "num", "files"), use_container_width=True)

# 保存ds数据
c1, c2, _ = st.columns([1, 2, 17])
c1.write("4.")
save_button = c2.button("保存")
if save_button:
    # 检查ds中的name和extractor是否含有空字符串
    empty_name = ds['name'].apply(lambda x: x == "").any()
    empty_extractor = ds['extractor'].apply(lambda x: x == "").any()
    if empty_name or empty_extractor:
        st.error("name或extractors不能为空！")
    elif ds['name'].duplicated().any():
        st.error("name不能重复！")
    else:
        save_data(ds)
        st.success(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]保存成功！可点击👈左侧的[🏷标注]进行标注。")