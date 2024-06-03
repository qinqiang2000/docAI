import json
import logging
import os
import time
from datetime import datetime

import streamlit as st
from streamlit import session_state as session
import pandas as pd
from streamlit_js_eval import streamlit_js_eval
import streamlit_antd_components as sac

from core.common import DATASET_DIR, DocLanguage, OCRProvider, LABEL_DIR
from core.extractor_manager import ExtractorManager
from core.llm.llm import LlmProvider
from file_server import port
from tools.utitls import custom_page_styles, display_image, separator, show_label_json

st.set_page_config(
    page_title="标注",
    page_icon="🏷️",
    layout="wide",
    menu_items={
        'About': "#💡 This is a header. This is an *extremely* cool app!"
    }
)

screen_height = streamlit_js_eval(js_expressions='screen.height', key='SCR')
height = None if not screen_height else screen_height - 100
hostname = streamlit_js_eval(js_expressions='window.location.hostname', key='hostname')

custom_page_styles(padding_top=0, height=height)
# 调整组件间隙
st.html(
    """
    <style>
    [data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
    </style>
    """
)

manager = ExtractorManager()

# 读取数据集
df = pd.read_csv(os.path.join(DATASET_DIR, "dataset.csv"))
dataset_names = df['name'].tolist()

if 'file_index' not in st.session_state:
    session['file_index'] = None

if not os.path.exists(LABEL_DIR):
    os.makedirs(LABEL_DIR)


def display_pdf(file_path):
    # 获取file_path的文件名字
    filename = file_path.split("/")[-1]
    pdf_url = f"http://{hostname}:{port}/files?fn={DATASET_DIR}/{session['dataset_id']}/{filename}"
    pdf_display = f'<embed src="{pdf_url}" type="application/pdf" width="100%" height={height} />'
    st.markdown(pdf_display, unsafe_allow_html=True)


# 外部导入已标注数据，格式需和本模块要求的一致
@st.experimental_dialog("导入标注数据")
def import_label_data(dataset, extractor):
    file = st.file_uploader("上传CSV或Excel文件", type=["csv", "xlsx"])
    if not file:
        return

    data = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)

    # 检查缺少的字段
    fields = extractor.fields
    fields['file_name'] = None
    fields['page_no'] = None
    missing_fields = [field for field in fields if field not in data.columns]
    if missing_fields:
        st.error(f"缺少字段: {', '.join(missing_fields)}")
        return

    data = data.filter(items=fields.keys())

    st.success("字段检查通过，数据预览:")
    st.write(data.head())

    if st.button("确认导入"):
        grouped = data.groupby('file_name')
        for file_name, group in grouped:
            # 调用save_one_file_label函数保存数据
            save_one_file_label(group, dataset, file_name, persist=True)

        st.success("导入成功")
        time.sleep(2)
        st.rerun()


def process_file(fn):
    file_path = os.path.join(DATASET_DIR, session['dataset_id'], fn)
    ret = load_file_label_data(file_path)
    if ret is None:
        logging.info(f"extract: {file_path}")
        extractor = manager.get_extractor(session['extractor'])
        ret = extractor.run(file_path, None, llm_provider=LlmProvider.MOCK, ocr_provider=OCRProvider.MOCK)

    session['labelling_data'] = ret  # 将数据存储在session_state中


def auto_label(fn):
    file_path = os.path.join(DATASET_DIR, session['dataset_id'], fn)

    extractor = manager.get_extractor(session['extractor'])
    ret = extractor.run(file_path, None, llm_provider=LlmProvider.LLaMA3_70b_GROQ, ocr_provider=OCRProvider.REGENAI_DOC_HACK)

    session['labelling_data'] = ret
    st.rerun()


def on_file_change():
    fn = session['selectbox_file']
    print(fn)
    if fn:
        process_file(fn)


# 加载文件已标注的数据，如果未标注过，返回True
def load_file_label_data(file_path):
    filename = os.path.basename(file_path)
    ret = None
    # 检查是否已经存在标签数据
    if session['label_data'] is not None:
        # 找到与当前文件名匹配的行
        matched_rows = session['label_data'][session['label_data']['file_name'] == filename]
        if not matched_rows.empty:
            # 如果找到匹配的行，将这些行的数据添加到data_str_list中
            matched_rows = matched_rows.drop(columns=['file_name', 'page_no']).to_dict('records')
            labels = []
            for r in matched_rows:
                p = json.loads(r['label'])
                labels.append(p)
            ret = labels

    return ret


def load_label_data(dataset_name):
    # 已经加载过数据集，不需要再次加载
    if 'dataset_id' in st.session_state and session['dataset_name'] == dataset_name:
        return

    file_path = os.path.join(LABEL_DIR, f"{dataset_name}.csv")
    if os.path.exists(file_path):
        session['label_data'] = pd.read_csv(file_path)
    else:
        session['label_data'] = None
        logging.info(f"文件 {file_path} 不存在")


def save_one_file_label(new_data, dataset_name, filename, persist=True):
    if 'label_data' in st.session_state and session['label_data'] is not None:
        # 如果label_data已经存在，我们需要删除相应的行
        session['label_data'] = session['label_data'].loc[
            ~((session['label_data']['file_name'] == filename) & (session['label_data']['page_no'].isin(new_data['page_no'])))]
        # 然后添加新的标签数据到最前面
        session['label_data'] = pd.concat([new_data, session['label_data']], ignore_index=True)
    else:
        # 如果label_data不存在，我们只需将新数据添加到label_data中
        session['label_data'] = new_data

    if not persist:
        return

    # 保存label_data到CSV文件
    csv_file_path = os.path.join(LABEL_DIR, f"{dataset_name}.csv")
    session['label_data'].to_csv(csv_file_path, index=False)


def save_manual_labels(labeled_data, filename, dataset_name, persist=True):
    data_list = []
    for i, page_data in enumerate(labeled_data):
        data_dict = {'file_name': filename, 'page_no': i + 1}
        label = page_data
        try:
            json.loads(label)
        except Exception as e:
            st.write(f"第{i+1}页的标注数据格式异常: {e}")
            label = []
        data_dict['label'] = label
        data_list.append(data_dict)

    new_data = pd.DataFrame(data_list)
    save_one_file_label(new_data, dataset_name, filename, persist=persist)


# --- 侧边栏 ---
with st.sidebar:
    st.caption("⚠️不能多人同时标注同一数据集")

    selected_dataset = st.selectbox('数据集', dataset_names)
    if selected_dataset:
        # 读取已标注数据
        load_label_data(selected_dataset)

        # 读取数据集信息
        session['dataset_name'] = selected_dataset
        row = df[df['name'] == selected_dataset]
        session['dataset_id'] = row['id'].values[0]
        session['extractor'] = row['extractor'].values[0]
        selected_files = row['files'].values[0].split(separator)
        session['file_list'] = [file.strip() for file in selected_files]
        st.selectbox('文件列表', session['file_list'], key='selectbox_file',
                     index=session['file_index'], on_change=on_file_change)

        doc_language = st.selectbox("数据集语言", options=[e.value for e in DocLanguage],
                                    help="自动标注且需要OCR时，选择")
        session["selected_lang"] = next(e for e in DocLanguage if e.value == doc_language)

    if selected_dataset:
        if st.button("导入", help="从外部导入已标注的数据"):
            import_label_data(selected_dataset, manager.get_extractor(session['extractor']))

# --- 主区域 ---
col1, col2 = st.columns([0.65, 0.35])
if not session['selectbox_file']:
    st.warning("👈请从左侧选择要标注的文件")
# 主区域的左面板
with col1.container():
    if 'selectbox_file' in st.session_state and session['selectbox_file']:
        selected_file = session['selectbox_file']
        file_path = os.path.join(DATASET_DIR, session['dataset_id'], selected_file)
        if os.path.exists(file_path):
            if file_path.lower().endswith('.pdf'):
                display_pdf(file_path)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                display_image(file_path)
            else:
                st.write(f"文件类型 {file_path} 不支持")
        else:
            col1.warning(f"文件 {selected_file} 不存在")

# 主区域的右面板
with col2.container():
    if session['selectbox_file']:
        st.write("正在标注: ", session['selectbox_file'])
        st.caption("注：以json数组格式标注")

    if 'labelling_data' in st.session_state:
        _files = session['file_list']
        i = _files.index(session['selectbox_file'])

        labeled_data = show_label_json(session['labelling_data'], "json")
        msg_placeholder = st.empty()

        if st.button(f"下一个({i + 1}/{len(_files)})"):
            i = (i + 1) % len(_files)
            session['file_index'] = i
            process_file(_files[i])
            st.rerun()
        if st.button("保存", key="save_1"):
            save_manual_labels(labeled_data, session['selectbox_file'], selected_dataset)
            msg_placeholder.success(f"保存数据集[{selected_dataset}]成功")
            # todo:借助on_file_change函数更新数据(待优化)
            on_file_change()
            time.sleep(3)
            msg_placeholder.empty()
        if st.button("自动标注"):
            auto_label(_files[i])

# 主页面底部
expander = st.expander(f"Label result of dataset [{selected_dataset}]", expanded=False)
with expander:
    if 'label_data' in st.session_state and session['label_data'] is not None:
        # 获取原始列名
        cols = session['label_data'].columns.tolist()
        # 移除'file_name'和'page_no'
        cols.remove('file_name')
        cols.remove('page_no')
        # 将'file_name'和'page_no'添加到列名列表的前面
        cols = ['file_name', 'page_no'] + cols
        # 使用新的列顺序重新索引DataFrame
        df_display = session['label_data'].reindex(columns=cols)

        # df_display = st.data_editor(df_display, use_container_width=True, hide_index=True)
        if st.button("保存") and df_display is not None:
            # 保存label_data到CSV文件
            csv_file_path = os.path.join(LABEL_DIR, f"{selected_dataset}.csv")
            session['label_data'] = df_display
            session['label_data'].to_csv(csv_file_path, index=False)
            st.success(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]保存数据集[{selected_dataset}]成功")
    else:
        st.write("No label data available.")
