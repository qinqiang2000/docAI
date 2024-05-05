import streamlit as st
import pandas as pd
import json
import os
import time  # Add this import if it's not already in your script

# Persistent storage file
EXTRACTORS_FILE = 'data/extractors.json'

st.set_page_config(page_title="提取器配置", page_icon="🔍")
st.title("提取器配置")


def load_extractors():
    if os.path.exists(EXTRACTORS_FILE):
        with open(EXTRACTORS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_extractor(name, description, fields):
    extractors = load_extractors()
    extractors[name] = {'description': description, 'fields': fields}
    with open(EXTRACTORS_FILE, 'w') as f:
        json.dump(extractors, f, indent=4, ensure_ascii=False)

def delete_extractor(name):
    extractors = load_extractors()
    if name in extractors:
        del extractors[name]
        with open(EXTRACTORS_FILE, 'w') as f:
            json.dump(extractors, f, indent=4, ensure_ascii=False)
        return True
    return False

def save_data(name, description, fields, rerun=False):
    if not name or not description:
        st.error("Both '名字' and '描述' must be filled out.")
    else:
        # Use attribute access on namedtuples for fields
        fields_dict = {row.Field: row.Description for row in fields.itertuples(index=False)}
        save_extractor(name, description, fields_dict)
        st.success(f"Extractor '{name}' has been saved!")
        st.session_state.selected_extractor = name
        st.session_state.state = None
        if rerun:
            time.sleep(3)  # Wait for 3 seconds
            st.rerun()

def load_data(extractor=None):
    if extractor:
        fields = [{"Field": key, "Description": value} for key, value in extractor['fields'].items()]
    else:
        fields = [{"Field": "", "Description": ""}]
    return pd.DataFrame(fields)


if 'state' not in st.session_state:
    st.session_state.state = None

with st.sidebar:
    extractors = load_extractors()
    extractor_names = list(extractors.keys())
    default_index = 0  # Set to the first item, or another safe default
    selected_extractor_name = st.session_state.get('selected_extractor', '')
    if selected_extractor_name in extractor_names:
        default_index = extractor_names.index(selected_extractor_name)
    selected_extractor = st.selectbox("提取器列表", options=extractor_names, index=default_index)
    new_extractor = st.button("新建")

# When an extractor is selected from the sidebar
if selected_extractor and not new_extractor and st.session_state.state != "new":
    st.session_state.state = "view"
    extractor_details = extractors[selected_extractor]
    name = st.text_input("名字", value=selected_extractor, key="view_name", disabled=True)
    description = st.text_area("描述", value=extractor_details['description'], key="view_description")
    fields = st.data_editor(data=load_data(extractor_details), column_config={"Field": "字段", "Description": "描述"},
                   num_rows="dynamic", use_container_width=True)

    if st.button("Save"):
        save_data(name, description, fields)
    elif st.button("Delete", key="Delete"):
        if delete_extractor(selected_extractor):
            st.success(f"Extractor '{selected_extractor}' has been deleted!")
            time.sleep(3)  # Wait for 3 seconds
            st.session_state.state = None
            st.rerun()


# Creating or editing an extractor
if new_extractor or st.session_state.state == "new":
    st.session_state.state = "new"
    name = st.text_input("名字", key="name")
    description = st.text_area("描述", key="description")

    st.write("字段列表")
    fields = st.data_editor(data=load_data(), column_config={
        "Field": "字段",
        "Description": "描述",
    }, num_rows="dynamic", use_container_width=True)

    if st.button("Save"):
        save_data(name, description, fields, rerun=True)
