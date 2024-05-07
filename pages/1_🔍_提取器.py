import streamlit as st
import pandas as pd
import time

from core.extractor import Extractor
from core.extractor_manager import ExtractorManager

# Create an instance of the manager
manager = ExtractorManager()

st.set_page_config(page_title="提取器配置", page_icon="🔍")
st.title("提取器配置")


def save_data(name, description, fields, rerun=False):
    if not name or not description:
        st.error("Both '名字' and '描述' must be filled out.")
    else:
        fields_dict = {row.Field: row.Description for row in fields.itertuples(index=False)}
        extractor = Extractor(name, description, fields_dict)  # Create an Extractor instance
        manager.save_extractor(extractor)  # Assuming save_extractor accepts an Extractor instance
        st.success(f"Extractor '{name}' has been saved!")
        st.session_state.selected_extractor = name
        st.session_state.state = None
        if rerun:
            time.sleep(3)
            st.rerun()


def load_data(extractor=None):
    if extractor and extractor.fields:
        # Assuming fields are a dictionary like {'field_name': 'field_description'}
        fields = [{"Field": key, "Description": value} for key, value in extractor.fields.items()]
    else:
        # Create an empty DataFrame with specified columns when there are no fields
        fields = [{"Field": "", "Description": ""}]
    # Provide an empty index if fields are empty, which is suitable for creating an empty DataFrame
    return pd.DataFrame(fields)


if 'state' not in st.session_state:
    st.session_state.state = None

with st.sidebar:
    extractor_names = manager.get_extractors_list()
    default_index = 0  # Set to the first item, or another safe default
    selected_extractor_name = st.session_state.get('selected_extractor', '')
    if selected_extractor_name in extractor_names:
        default_index = extractor_names.index(selected_extractor_name)
    selected_extractor = st.selectbox("提取器列表", options=extractor_names, index=default_index)
    new_extractor = st.button("新建")

# When an core is selected from the sidebar
if selected_extractor and not new_extractor and st.session_state.state != "new":
    st.session_state.state = "view"
    extractor = manager.get_extractor(selected_extractor)
    name = st.text_input("名字", value=selected_extractor, key="view_name", disabled=True)
    description = st.text_area("描述", value=extractor.description, key="view_description", height=300)
    _fields = load_data(extractor)
    fields = st.data_editor(data=_fields, column_config={"Field": "字段", "Description": "描述"},
                   num_rows="dynamic", use_container_width=True)

    c1, c2, c3, _ = st.columns([1, 1, 1, 7])
    if c1.button("Save"):
        save_data(name, description, fields)
    elif c2.button("Delete", key="Delete"):
        if manager.delete_extractor(selected_extractor):
            st.success(f"Extractor '{selected_extractor}' has been deleted!")
            st.session_state.state = None
            time.sleep(2)
            st.rerun()


# Creating or editing an core
if new_extractor or st.session_state.state == "new":
    st.session_state.state = "new"
    name = st.text_input("名字", key="name")
    description = st.text_area("描述", key="description", height=200)

    st.write("字段列表")
    fields = st.data_editor(data=load_data(), column_config={
        "Field": "字段",
        "Description": "描述",
    }, num_rows="dynamic", use_container_width=True)

    if st.button("Save"):
        save_data(name, description, fields, rerun=True)
