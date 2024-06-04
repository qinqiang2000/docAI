import streamlit as st
import pandas as pd
import json

# 示例DataFrame
df = pd.DataFrame({
    'filename': ['file1.txt', ],
    'label1': [json.dumps({"key1": "value1", "key2": "value2"})],
    'label2': [json.dumps({"key3": "value3"})]
})

# 将DataFrame转换为表格
st.write("### JSON Data in Table")
table = st.table(df)

# 展示JSON数据
for index, row in df.iterrows():
    filename = row['filename']
    label1 = row['label1']
    label2 = row['label2']

    # 使用Markdown代码块来展示JSON数据
    st.markdown(f"**Filename:** `{filename}`")
    st.markdown(f"**Label1:**\n```json\n{label1}\n```")
    st.markdown(f"**Label2:**\n```json\n{label2}\n```")