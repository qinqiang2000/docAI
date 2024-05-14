import streamlit as st
import pandas as pd
import time

from core.extractor import Extractor
from core.extractor_manager import ExtractorManager

# Create an instance of the extractor manager
manager = ExtractorManager()

st.set_page_config(page_title="提取器配置", page_icon="🔍")
st.title("提取器配置")


def save_data(old_name, name, description, fields, rerun=False):
    if not name or not description:
        st.error("Both '名字' and '描述' must be filled out.")
    else:
        fields_dict = {row.Field: row.Description for row in fields.itertuples(index=False)}
        extractor = Extractor(name, description, fields_dict)  # Create an Extractor instance
        manager.save_extractor(extractor)  # Assuming save_extractor accepts an Extractor instance
        st.success(f"Extractor '{name}' has been saved!")

        st.session_state.selected_extractor = name
        st.session_state.state = None

        # 删除老的extractor
        if old_name:
            if manager.delete_extractor(old_name):
                print(f"Old extractor: {old_name} deleted successfully!")
            else:
                print(f"Old extractor: {old_name} deleted failed!")

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


def on_change():
    st.session_state.state = None

@st.experimental_dialog("确认删除？")
def confirm_del(name):
    st.write(f"Are you sure you want to delete {name}?")
    if st.button("Submit"):
        st.session_state['delete'] = name
        st.rerun()


if 'state' not in st.session_state:
    st.session_state.state = None
    new_extractor = None

with st.sidebar:
    extractor_names = manager.get_extractors_list()
    default_index = 0  # Set to the first item, or another safe default
    selected_extractor_name = st.session_state.get('selected_extractor', '')
    if selected_extractor_name in extractor_names:
        default_index = extractor_names.index(selected_extractor_name)
    selected_extractor = st.selectbox("提取器列表", options=extractor_names, index=default_index,
                                      on_change=on_change)
    new_extractor = st.button("新建")

# When a core is selected from the sidebar
if selected_extractor and not new_extractor and st.session_state.state != "new":
    st.session_state.state = "view"
    extractor = manager.get_extractor(selected_extractor)
    name = st.text_input("名字", value=selected_extractor, key="view_name")
    description = st.text_area("描述", value=extractor.description, key="view_description", height=300)
    _fields = load_data(extractor)
    fields = st.data_editor(data=_fields, column_config={"Field": "字段", "Description": "描述"},
                            num_rows="dynamic", use_container_width=True)

    c1, c2, c3, _ = st.columns([1, 1, 1, 5])
    if c1.button("Save"):
        save_data(selected_extractor, name, description, fields, True)
    elif c2.button("Delete", key="Delete"):
        confirm_del(selected_extractor)
        if st.session_state['delete'] == selected_extractor and manager.delete_extractor(selected_extractor):
            st.session_state.state = None
            st.session_state['delete'] = None
            st.rerun()

# Creating or editing a core
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
        save_data(None, name, description, fields, rerun=True)
