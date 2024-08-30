import json
import logging
from datetime import datetime

import streamlit as st
import pandas as pd
import os

from streamlit_js_eval import streamlit_js_eval

from core.common import EVALUATE_DIR, OCRProvider, LABEL_DIR, DATASET_DIR, DocLanguage
from core.evaluator.json_custom_evl import evaluate_json_str, evaluate_json
from core.extractor_manager import ExtractorManager  # Ensure the correct path
from core.llm.llm import LlmProvider
from file_server import port
from tools.utitls import display_image

st.set_page_config(
    page_title="评估", page_icon="📝", layout="wide",
    menu_items={'About': "#📝 This is a header. This is an *extremely* cool app!"}
)

hostname = streamlit_js_eval(js_expressions='window.location.hostname', key='hostname')

task_data_file = os.path.join(EVALUATE_DIR, "task.csv")

result_colum_suffix = '__r'


# 获取指定目录下的所有 CSV 文件名，不包含扩展名
def get_dataset_name():
    if "data" in st.session_state:
        df = st.session_state['data']
        return df['name'].unique()


def load_data():
    st.session_state['task'] = pd.read_csv(os.path.join(EVALUATE_DIR, "task.csv"))  # 标注任务
    st.session_state['data'] = pd.read_csv(os.path.join(DATASET_DIR, "dataset.csv"))  # 数据集


def save_task(df):
    empty_name = df['name'].apply(lambda x: x == "").any()
    empty_llm = df['llm'].apply(lambda x: x == "").any()
    empty_ocr = df['ocr'].apply(lambda x: x == "").any()
    empty_label_set = df['label_set'].apply(lambda x: x == "").any()
    if empty_name or empty_llm or empty_ocr or empty_label_set:
        st.error("未填写必填项")
        return False
    if df['name'].duplicated().any():
        st.error("name不能重复！")
        return False

    df.to_csv(task_data_file, index=False)
    st.session_state.task = df
    return True


def dataframe_with_selections(df, colum_cfg, num_rows="dynamic"):
    df_with_selections = df.copy()
    if 'Select' not in df_with_selections.columns:
        df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(data=df_with_selections, column_config=colum_cfg,
                               hide_index=True, num_rows=num_rows, use_container_width=True)

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1), edited_df


def update_task_time(task):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.session_state.task.loc[st.session_state.task['name'] == task['name'], 'time'] = current_time
    save_task(st.session_state.task)


def get_label_set(name):
    label_file_path = os.path.join(LABEL_DIR, f"{name}.csv")
    if not os.path.exists(label_file_path):
        st.error(f"没有找到与任务名 {name} 对应的标签文件。")
        return None
    return pd.read_csv(label_file_path)


# 对测试集files进行处理，返回提取结果
def run(files, task, extractor):
    for file_path in files:
        if not os.path.exists(file_path):
            st.warning(f"文件 {file_path} 不存在，跳过。")
            continue

        # 调用 extractor 的 run 接口
        extraction_result = extractor.run(
            file_path=file_path,
            stream_callback=None,
            llm_provider=LlmProvider[task['llm']],
            ocr_provider=OCRProvider[task['ocr']],
            lang=DocLanguage[task['lang']]
        )

        # 处理每个文件的提取结果，增加 file_name 和 page_no 列
        for page_no, page_result in enumerate(extraction_result, start=1):
            result_dict = {
                "file_name": os.path.basename(file_path),
                "page_no": page_no,
                "label": json.dumps(page_result, indent=2, ensure_ascii=False)
            }
            yield result_dict


def get_dataset(task):
    label_set_name = task['label_set']
    matching_data = st.session_state['data'][st.session_state['data']['name'] == label_set_name]
    return matching_data

def show_file_preview(url):
    if url.lower().endswith('.pdf'):
        pdf_display = f'<embed src="{url}" type="application/pdf" width="100%" />'
        st.markdown(pdf_display, unsafe_allow_html=True)
    elif url.lower().endswith(('.png', '.jpg', '.jpeg')):
        st.image(url)

def run_test(task):
    label_set_name = task['label_set']

    # 从数据集中取出 name 等于 task['name'] 的行
    matching_data = get_dataset(task)
    if matching_data.empty:
        st.error(f"没有找到与任务名 {label_set_name} 匹配的数据。")
        return None

    extractor_value = matching_data['extractor'].values[0]
    dataset_id = matching_data['id'].values[0]

    # 通过 extractor 的值和 ExtractorManager 的 get_extractor 获取 extractor 对象
    extractor = manager.get_extractor(extractor_value)

    # 读取对应的标注结果
    label_df = get_label_set(label_set_name)

    # 遍历 label_df 的 file_name（去重），每个 file 的全路径是 DATASET_DIR/{id}/{file_name}
    files = [os.path.join(DATASET_DIR, str(dataset_id), file_name)
            for file_name in label_df['file_name'].drop_duplicates()]

    # 处理指定测试集
    results = []
    # result_placeholder = st.empty()  # 用于显示动态更新的结果
    for result in run(files, task, extractor):
        results.append(result)
        result_df = pd.DataFrame(results)
        st.session_state['evl_result_ph'].dataframe(result_df, hide_index=True, use_container_width=True)

    update_task_time(task)

    return results


def save_task_result(task, results_df, test=True):
    path = os.path.join(EVALUATE_DIR, "result")
    os.makedirs(path, exist_ok=True)

    if test:
        filename = f"/{task['name']}_test.csv"
    else:
        filename = f"/{task['name']}_evl.csv"

    results_df.to_csv(path + filename, index=False)


def show_task_result(task):
    path = os.path.join(EVALUATE_DIR, "result")
    test_file = os.path.join(path, f"{task['name']}_test.csv")

    if not os.path.exists(test_file):
        return False

    test_df = pd.read_csv(test_file)

    label_df = get_label_set(task['label_set'])
    evl_df = evaluate_results(label_df, test_df)

    st.markdown(f"##### 任务'{task['name']}'的评估结果")
    show_evl_metrics(evl_df)
    show_evl_tbl(task, evl_df)


def evaluate_results(df_label, df_test):
    # 仅保留label_df的列
    df_right = df_test[df_label.columns]

    # 合并两个 DataFrame，依据列 'a' 和 'b' 进行左连接
    df = pd.merge(df_label, df_right, on=['file_name', 'page_no'], how='left', suffixes=('', '_t'))

    # 提取 file_name 和 page_no 列
    file_name_col = df['file_name']
    page_no_col = df['page_no']

    # 初始化一个空的 DataFrame 来存储最终结果
    df_result = pd.DataFrame()

    # 按照原始顺序创建新的列顺序，并生成比较结果列
    for column in df.columns:
        if column in ['file_name', 'page_no']:
            continue
        if '_t' not in column:
            test_column = f"{column}_t"
            score_column = f"score"
            neg_column = f"neg"
            # 执行评估
            df["tmp"] = df.apply(lambda row: evaluate_json_str(row[test_column], row[column]), axis=1)
            df[score_column] = df["tmp"].apply(lambda x: x['score'])
            df[neg_column] = df["tmp"].apply(lambda x: str(x['negative']))
            df_result[score_column] = df[score_column]
            df_result[column] = df[column]
            df_result[test_column] = df[test_column]
            df_result[neg_column] = df[neg_column]

    # 将 file_name 和 page_no 列添加回结果 DataFrame 的开头
    df_result.insert(0, 'page_no', page_no_col)
    df_result.insert(0, 'file_name', file_name_col)

    return df_result


def show_evl_tbl(task, df_result):
    # 做表格的一些特殊处理便于显示 todo: 异常处理
    df_display = df_result.copy()
    tid = get_dataset(task)['id'].values[0]

    # file_name做成文件查看超链接
    df_display['file_name'] = df_result['file_name'].apply(lambda x: f"http://{hostname}:{port}/files?fn=data/dataset/{tid}/{x}")
    cc = {"file_name": st.column_config.LinkColumn(display_text=f"data/dataset/{tid}/(.*?)$")}

    # # 添加一个状态列
    # df_display['status'] = df_result.apply(lambda row: all(row[col] for col in df_result.columns if col.endswith('__r')), axis=1)
    # df_display = df_display[['status'] + [col for col in df_display.columns if col != 'status']]
    #
    # # 将 True 和 False 替换为 ✔️ 和 ❌
    # comparison_columns = [col for col in df_display.columns if col.endswith('__r')]
    # for col in comparison_columns:
    #     df_display[col] = df_display[col].apply(lambda x: '✔️' if x else '❌')

    # 格式化 JSON 字符串
    def format_json(json_str):
        if not isinstance(json_str, str):
            return json_str
        try:
            parsed = json.loads(json_str)
            return json.dumps(parsed, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            return json_str

    # 应用格式化函数到 DataFrame
    df_formatted = df_display.map(format_json)

    st.write("明细")
    sel, ds = dataframe_with_selections(df_formatted, cc, "fixed")
    if sel.empty:
        return

    label = sel['label'].iloc[-1]
    label_t = sel['label_t'].iloc[-1]
    label_neg = sel['neg'].iloc[-1]
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        st.caption("label(标注)")
        st.json(label)
    with c2:
        st.caption("test(测试)")
        st.json(label_t)
    with c3:
        st.caption("neg(差异)")
        st.json(label_neg)

    show_file_preview(sel['file_name'].iloc[-1])

    # st.data_editor(df_formatted, column_config=cc,   hide_index=True, use_container_width=True)


def show_evl_metrics(evl_df):
    # 提取以result_colum_suffix结尾的列进行统计
    # comparison_columns = [col for col in evl_df.columns if col.endswith(result_colum_suffix)]

    # 计算总体准确率
    total_correct = evl_df['score'].sum()
    total_accuracy = total_correct / float(len(evl_df))

    # 计算每一列准确率
    # column_accuracies = evl_df[comparison_columns].mean()

    # 展示总体准确率
    st.metric(label="总体准确率", value=f"{total_accuracy:.2%}")

    # # 展示每一列准确率
    # column_accuracies.index = column_accuracies.index.str.replace(result_colum_suffix, '')
    # column_accuracies = column_accuracies * 100
    # st.write("字段准确率(%)")
    # st.bar_chart(column_accuracies)


def evaluate(task):
    # 执行测试任务，获取测试结果
    run_result = run_test(task)
    if not run_result:
        return

    # 保存测试结果
    save_task_result(task, pd.DataFrame(run_result))

    # 读取标注结果
    label_df = get_label_set(task['label_set'])

    # 评估
    evl_df = evaluate_results(label_df, pd.DataFrame(run_result))
    # 保存评估结果
    save_task_result(task, evl_df, test=False)

    # 展示
    show_evl_metrics(evl_df)
    show_evl_tbl(task, evl_df)


# Initialize the ExtractorManager
manager = ExtractorManager()

task_colum = {
    "Select": st.column_config.CheckboxColumn(label='选择', help="尽量单选", default=False, required=True),
    "name": st.column_config.TextColumn(label='任务名', help="填写任务名称", required=True,),
    "label_set": st.column_config.SelectboxColumn(
            label='验证集', help="已标注的数据集", width="medium", options=get_dataset_name(), required=True,),
    "llm": st.column_config.SelectboxColumn(
            label='LLM', help="已标注的数据集", width="medium", options=list(LlmProvider.__members__.keys()),required=True),
    "ocr": st.column_config.SelectboxColumn(
            label='OCR', help="选择OCR模块", width="medium", options=list(OCRProvider.__members__.keys()), required=True),
    "lang": st.column_config.SelectboxColumn(
            label='语种', help="数据集主要语言", width="medium", options=list(DocLanguage.__members__.keys()), required=True),
    "time": st.column_config.Column(label='执行时间', help="执行时间", disabled=True,),
}

load_data()

# Display the task table editor
st.write("评估任务列表")
selection, ds = dataframe_with_selections(st.session_state.task, task_colum)

sel_name = None
if not selection.empty:
    sel_name = selection['name'].iloc[-1]  # 获取 selection 的最后一行的 name
    st.caption(f"已选中: {sel_name}")

c1, c2, c3 = st.columns([1, 1, 10])
save_button = c1.button("保存")
if save_button:
    if save_task(ds):
        print("="*9, "\n", ds)
        st.success(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]保存成功！")
if not selection.empty:
    task = selection.iloc[-1]
    if c2.button(f"执行"):
        evaluate(task)
    else:
        show_task_result(task)
    st.session_state['evl_result_ph'] = st.empty()


