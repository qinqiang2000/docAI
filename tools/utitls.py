import streamlit as st
from PIL import Image

separator = "|"


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


def wide_styles():
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