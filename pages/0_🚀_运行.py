import pandas as pd
import streamlit as st
from streamlit import session_state as session
from streamlit_js_eval import streamlit_js_eval
from streamlit_pdf_reader import pdf_reader
from core.extractor_manager import ExtractorManager
from core.common import LlmProvider, OCRProvider, DocLanguage
from PIL import Image
from file_server import save_uploaded_file, port

st.set_page_config(
    page_title="运行",
    page_icon="🚀",
    layout="wide",
    menu_items={
        'About': "#💡 This is a header. This is an *extremely* cool app!"
    }
)

# 自定义CSS来减少边距和填充
st.markdown("""
<style>
/* 用于整个页面的块容器的样式 */
[data-testid="stAppViewBlockContainer"] {
    padding-top: 1rem;
    padding-right: 1rem; /* 右边距 */
    padding-left: 1rem; /* 左边距 */
    padding-bottom: 0rem;
}
[data-testid="stDataFrame"]  {
    white-space: pre-wrap; /* CSS property to make whitespace significant */
}
</style>
""", unsafe_allow_html=True)

screen_height = streamlit_js_eval(js_expressions='screen.height', key='SCR')
height = None if not screen_height else screen_height - 100
hostname = streamlit_js_eval(js_expressions='window.location.hostname', key='hostname')

# Create an instance of the manager
manager = ExtractorManager()

if 'text' not in session:
    session['text'] = ""


# 定制表格列style
def style_columns(df):
    def key_text_color(val):
        return 'color: black'

    def val_text_color(val):
        return 'color: #2b66c2'

    return (df.style
            .map(key_text_color, subset=['key'])  # Using .map for column-wise styling
            .map(val_text_color, subset=['value']))


def handle_file_upload():
    if session['uploaded_file'] is None:
        session.pop('text', None)  # Safely remove 'text' if it exists, do nothing if it doesn't
        session.pop('data', None)  # Safely remove 'data' if it exists, do nothing if it doesn't
        session.pop('file_index', 0)
    else:
        session['file_index'] = 0


def steam_callback(chuck):
    session['text'] += chuck
    if session["result_placeholder"]:
        session["result_placeholder"].markdown(session['text'])


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


def display_pdf(file_path):
    # 获取file_path的文件名字
    filename = file_path.split("/")[-1]
    pdf_url = f"http://{hostname}:{port}/{filename}"
    pdf_display = f'<embed src="{pdf_url}" type="application/pdf" width="100%" height={height} />'
    # f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height={height} type="application/pdf">'
    st.markdown(pdf_display, unsafe_allow_html=True)


def display_process(file):
    file_path = save_uploaded_file(file)

    if "pdf" in file.type:
        # pdf_reader(file)  # display file
        display_pdf(file_path)  # display file
    elif "image" in file.type:
        display_image(file)
    else:
        st.warning("Unsupported file type")
        return

    session['text'] = ""  # clear text
    session['data'] = []

    if not session['selected_extractor'] or len(session['selected_extractor']) <= 0:
        st.warning("No extractor selected")
        return

    for option in session['selected_extractor']:
        extractor = manager.get_extractor(option)
        data_list = extractor.run(file_path, steam_callback, llm_provider=session["selected_llm_provider"],
                                  ocr_provider=session["selected_ocr_provider"], lang=session["selected_lang"])
        data_str_list = []
        for data in data_list:
            data_str = [{k: str(v) for k, v in item.items()} for item in data]  # 将数据转换为字符串以确保兼容性
            data_str_list.append(data_str)

        session['data'].append((option, data_str_list))  # 将数据存储在session_state中


# 侧边栏
with st.sidebar:
    _files = st.file_uploader("Choose a file", type=['pdf', 'jpg', 'jpeg', 'png'], key='uploaded_file',
                              on_change=handle_file_upload, accept_multiple_files=True, label_visibility='collapsed')
    # Dropdown for selecting an extractor
    available_extractors = manager.get_extractors_list()
    session['selected_extractor'] = st.multiselect("提取器", options=available_extractors,
                                                   default=available_extractors[0],
                                                   help="文档有混合要素时(如水费+电费)，可选择多个提取器")

    llm_provider = st.selectbox("LLM", options=list(LlmProvider.__members__.keys()))
    session["selected_llm_provider"] = LlmProvider[llm_provider]

    ocr_provider = st.selectbox("OCR", options=list(OCRProvider.__members__.keys()), help="图片类文件才需OCR")
    session["selected_ocr_provider"] = OCRProvider[ocr_provider]

    doc_language = st.selectbox("文档主要语种", options=[e.value for e in DocLanguage],
                                help="部分OCR模块需指定语言；混合语言者，选占比最多的语种")
    session["selected_lang"] = next(e for e in DocLanguage if e.value == doc_language)

cols = [0.65, 0.35]
col1, col2 = st.columns(cols)

# 左面板，预览PDF或图片
with col1.container():
    if _files is not None and len(_files) > 0:
        idx = session.get('file_index', 0)
        display_process(_files[idx])

column_config = {
    "key": st.column_config.TextColumn(
        "key", help="关键要素", width=None
    ),
    "value": st.column_config.TextColumn(
        "value", help="要素值", width="large"
    ),
}


def show_data(name, data_list):
    """
    显示提取的结构化数据。
    参数:
    name (str): 提取器的名称。
    data_list (list): 包含提取的数据的列表，每个元素是一个字典，表示一页的数据。
    """
    for i, page_data in enumerate(data_list):
        st.write("[", name, "]", "第", i + 1, "页")
        for item in page_data:
            df = pd.DataFrame(list(item.items()))
            df.columns = ['key', 'value']
            st.dataframe(style_columns(df), hide_index=True, use_container_width=True, column_config=column_config)


# 右面板，呈现数据
with col2.container(height=height, border=False):  # Adjusted for interface elements
    if 'data' in session:
        for name, data_list in session['data']:
            show_data(name, data_list)

        if st.button(f"下一个({session['file_index'] + 1}/{len(_files)})"):
            session['file_index'] = (session['file_index'] + 1) % len(_files)
            session.pop('rotated_image', None)
            st.rerun()

    # 流式呈现过程数据
    session["result_placeholder"] = st.empty()
    session["result_placeholder"].write(session['text'])
