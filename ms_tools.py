
import streamlit as st

# --- PAGE SETUP ---
about_page = st.Page(
    page  ='views/about_tools.py',
    title = "About tools",
    default = True
)

tool_1_page = st.Page(
    page  = "views/ms_viz_app.py",
    title = "data visualization"
)

tool_2_page = st.Page(
    page  = "views/ms_match_app.py",
    title = "ms match"
)

pg = st.navigation( 
    { "Info":  [about_page], "Tools": [tool_1_page, tool_2_page],})

pg.run()