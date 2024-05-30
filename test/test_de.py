import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    return pd.DataFrame(
        [
            {"command": "st.selectbox", "rating": 4, "is_widget": True},
            {"command": "st.balloons", "rating": 5, "is_widget": False},
            {"command": "st.time_input", "rating": 3, "is_widget": True},
        ]
    )


df = load_data()
edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

favorite_command = edited_df.loc[edited_df["rating"].idxmax()]["command"]
st.markdown(f"Your favorite command is **{favorite_command}** 🎈")

import streamlit as st
# from streamlit_extras.colored_header import colored_header
from streamlit_ace import st_ace

import json

# st.set_page_config(
#     page_title="JSON Editor",
#     page_icon="🌎 ",
# )

# colored_header(
#     label="JSON Editor",
#     description="Use this app to reformat and edit json files",
#     color_name="violet-70",
# )

THEMES = [
    "ambiance", "chaos", "chrome", "clouds", "clouds_midnight", "cobalt", "crimson_editor", "dawn",
    "dracula", "dreamweaver", "eclipse", "github", "gob", "gruvbox", "idle_fingers", "iplastic",
    "katzenmilch", "kr_theme", "kuroir", "merbivore", "merbivore_soft", "mono_industrial", "monokai",
    "nord_dark", "pastel_on_dark", "solarized_dark", "solarized_light", "sqlserver", "terminal",
    "textmate", "tomorrow", "tomorrow_night", "tomorrow_night_blue", "tomorrow_night_bright",
    "tomorrow_night_eighties", "twilight", "vibrant_ink", "xcode"
]

json_file = st.file_uploader("Upload JSON", type=["json"], )

col1, col2 = st.columns(2)
sep1 = col1.selectbox("Separators (1)", [",", ":", "="])
sep2 = col2.selectbox("Separators (2)", [":", ",", "="])
indents = col1.number_input("Indentation", min_value=1, value=4)
sort_keys = st.checkbox("Sort Keys", True)

if json_file:
    # with open(json_file) as f:
    temp = json.load(json_file)

    formatted = json.dumps(
        temp,
        indent=indents,
        sort_keys=sort_keys,
        separators=(f"{sep1}", f"{sep2}"),
        ensure_ascii=False
    )

    content = st_ace(
        value=formatted,
        language="json",
        # theme="solarized_dark",
        keybinding="vscode",
        min_lines=20,
        max_lines=None,
        font_size=13,
        tab_size=2,
        wrap=False,
        show_gutter=True,
        show_print_margin=False,
        readonly=False,
        annotations=None,
    )
    print(type(content))
    content

    st.download_button(
        label="Download formatted JSON",
        data=content,
        file_name='formatted.json',
        mime='json',
    )

else:
    st.warning("Upload a .json to get started")
