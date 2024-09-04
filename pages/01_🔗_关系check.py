import json
import os
import time

import streamlit as st
from openai import AzureOpenAI
from streamlit import session_state as session
from streamlit_agraph import agraph, Node, Edge, Config
from streamlit_js_eval import streamlit_js_eval

from core.common import OCRProvider, extract_json
from core.extractor_manager import ExtractorManager
from core.llm.llm import LlmProvider
from core.llm.llm_openai import LLMOpenAI
from file_server import save_uploaded_tmp_file
from tools.utitls import custom_page_styles

st.set_page_config(
    page_title="运行",
    page_icon="🚀",
    layout="wide",
    menu_items={
        'About': "#💡 This is a header. This is an *extremely* cool app!"
    }
)

EXTRACTOR_LLM = LlmProvider.AZURE_GPT4oMini
MATCH_LLM = LlmProvider.AZURE_GPT4oMini

# 自定义CSS来减少边距和填充
custom_page_styles(0)

screen_height = streamlit_js_eval(js_expressions='screen.height', key='SCR')
height = None if not screen_height else screen_height - 90
hostname = streamlit_js_eval(js_expressions='window.location.hostname', key='hostname')

if MATCH_LLM == LlmProvider.AZURE_GPT4o:
    azure_client = AzureOpenAI(
        api_key=os.environ['AZURE_OPENAI_API_KEY'],
        azure_endpoint="https://test-openai-service-wus3-rg4.openai.azure.com/",
        api_version="2024-05-01-preview"
    )
    azure_model = "gpt-4o"
else:
    azure_client = AzureOpenAI(
        api_key=os.environ['AZURE_OPENAI_GPT4oMINI_API_KEY'],
        api_version=os.environ['OPENAI_API_GPT4oMINI_VERSION'],
        azure_endpoint=os.environ['AZURE_OPENAI_GPT4oMINI_ENDPOINT']
        )
    azure_model = os.environ['OPENAI_GPT4OMIN_DEPLOYMENT_NAME']

# Create an instance of the manager
manager = ExtractorManager()

receipt_extractor = "结账单1"
inv_extractor = "大陆发票1"


def steam_callback(chuck):
    print(chuck, end="")
    session['text'] += chuck
    if "result_placeholder" in session:
        session['result_placeholder'].write(session['text'])


def process(file):
    file_path = save_uploaded_tmp_file(file)

    # 判断文件类型
    if "发票" in file.name:
        ext = inv_extractor
    else:
        ext = receipt_extractor

    _id = file_path.split("/")[-1].split(".")[0]
    if _id in session:
        time.sleep(1.5)
        return ext, file_path, [session[_id]]

    extractor = manager.get_extractor(ext)
    data_str_list = extractor.run(file_path, steam_callback, EXTRACTOR_LLM,
                                  ocr_provider=OCRProvider.REGENAI_DOC_HACK)

    return ext, file_path, data_str_list[0][0]


def build_relation(nodes):
    sys_prompt = """有多张发票和水单的结构化数据如下，请按如下规则找出发票和水单的匹配对：
1. 发票日期Invoice Date要大于等于水单日期
2.发票金额要小于等于水单金额

输出要求:
- 返回匹配上的发票和水单id对数组：[{"inv_id":"发票id","r_id":"水单id"}...]
- 确保JSON数组输出答案；确保用```json 和 ```标签包装答案。
- 只输出JSON数组，不要生成其他解释

    """
    edges = []

    inv_nodes = [n.to_dict().get("_data") for n in nodes if n.to_dict().get("_type") == inv_extractor]
    r_nodes = [n.to_dict().get("_data") for n in nodes if n.to_dict().get("_type") == receipt_extractor]

    text = f"\n发票数据：{inv_nodes}\n水单数据：{r_nodes}\n"
    print(text)

    _str = LLMOpenAI(azure_model, azure_client).generate_text(text, sys_prompt)

    match = extract_json(_str)
    for m in match[0]:
        edges.append(Edge(source=m['inv_id'],
                          label="一致",
                          target=m['r_id'],)
                     )

    print(edges)
    return edges


def save_data(_id, data):
    json_file = f"tmp/{_id}.json"
    with open(json_file, 'w') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


if 'nodes' not in session:
    session['nodes'] = []
if 'edges' not in session:
    session['edges'] = []

st.markdown("###  📝```Document Relationship Check``` ")
log_placeholder = st.empty()

# 侧边栏
with st.sidebar:
    _files = st.file_uploader("请上传发票或附件", type=['pdf', 'jpg', 'jpeg', 'png'], key='uploaded_file',
                              accept_multiple_files=True, label_visibility='collapsed')

    btn = st.button("运行", on_click=None)

cols = [0.65, 0.35]
col1, col2 = st.columns(cols)

if btn:
    session['nodes'] = []
    session['edges'] = []

if btn and _files and len(_files) > 0:
    st.sidebar.empty()

    for i, _file in enumerate(_files):
        log_placeholder.write(f"{i + 1}/{len(_files)}: 正在处理**{_file.name}**")
        session['text'] = ""

        option, file_path, data = process(_file)
        data = data[0]
        print(f"data_str_list: \n{data}")

        fn = file_path.split("/")[-1]
        _id = fn.split(".")[0]
        data["id"] = _id

        if option == inv_extractor:
            img = "inv.png"
            label = f"{data['Invoice Date']} ¥{data['Amount']}"
        else:
            img = "receipt.png"
            label = f"{data['日期']},¥{data['金额']}"

        session[_id] = data
        save_data(_id, data)

        # 添加节点
        session['nodes'].append(Node(id=_id,
                                     label=label,
                                     size=25,
                                     shape="circularImage",
                                     image=f"http://localhost:8090/files?fn=tmp/{img}",
                                     title=f"http://localhost:7860/preview?fn={fn}",
                                     _type=option,
                                     _data=data
                                     ),
                                )

    log_placeholder.write(f"正在检查{len(_files)}个节点的关系")
    session['edges'] = build_relation(session['nodes'])
    log_placeholder.markdown("```Completed```")

with col1:
    config = Config(width=750,
                    height=950,
                    directed=True,
                    physics=False,
                    hierarchical=False,
                    # **kwargs
                    )

    return_value = agraph(nodes=session['nodes'],
                          edges=session['edges'],
                          config=config)
with col2:
    session["result_placeholder"] = st.empty()
