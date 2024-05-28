import streamlit as st

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("## 欢迎使用```piaozone``` Document AI平台 👋")


st.markdown(
    """
    Document AI可以智能提取文档中的结构化信息，帮助您快速完成文档处理工作。
    ### 体验
    - 点击👈左侧"运行"，体验智能文档AI效果
    ### 想自定义提取要素?
    - 请点击👈左侧的 "提取器" 按钮
    ### 想评估模型的性能?
    - 请点击👈左侧的 "数据集" 按钮，创建要评估的数据集
    - 然后点击👈左侧的 "评估" 按钮
"""
)
