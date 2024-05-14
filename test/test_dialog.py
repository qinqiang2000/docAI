import streamlit as st
import pandas as pd

# 定义导入数据的函数
@st.experimental_dialog("Cast your vote")
def import_data():
    file = st.file_uploader("上传CSV或Excel文件", type=["csv", "xlsx"])
    if file:
        if file.name.endswith('.csv'):
            data = pd.read_csv(file)
        else:
            data = pd.read_excel(file)
        st.write("数据预览:", data.head())
        return data

# 主页面内容
st.title("数据导入示例")
if st.button("导入"):
    imported_data = import_data()
    if imported_data is not None:
        st.write("导入的数据信息：")
        st.dataframe(imported_data)
