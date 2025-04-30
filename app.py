import streamlit as st
import importlib.util
import sys
import os

# Set up the page
st.set_page_config(page_title="MS Tools", layout="wide")

# Define your navigation structure
nav_structure = {
    "Info": [
        {"title": "About tools", "path": "views/about_tools.py"}
    ],
    "Data Visualization": [
        {"title": "MS data plots", "path": "views/viz_tool/ms_viz_tab.py"},
        {"title": "fragment plots", "path": "views/viz_tool/fragment_viz.py"}
    ],
    "Tools for Intact RNA": [
        {"title": "mass match", "path": "views/intact_RNA/ms_match_app.py"},
        {"title": "homology search", "path": "views/intact_RNA/homology_search.py"}
    ],
    "Tools for Hydrolytic RNA": [
        {"title": "net generation", "path": "views/hydrolytic_RNA/basecall_net_download5.py"},
        {"title": "find fragments", "path": "views/hydrolytic_RNA/st_link_app.py"}
    ],
    "Sequence Tools": [
        {"title": "align sequences", "path": "views/seq_tools/seq_aln.py"},
        {"title": "reverse sequences", "path": "views/seq_tools/seq_rev.py"}
    ]
}


# Function to load and run a Python module from file path
def load_module(file_path):
    module_name = os.path.basename(file_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None:
        st.error(f"Could not find file: {file_path}")
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


# Initialize session state to track the current page
if 'current_page' not in st.session_state:
    st.session_state.current_page = "views/about_tools.py"  # Default page

# Create sidebar navigation
st.sidebar.title("MS Tools")

# Display the navigation menu
for section, pages in nav_structure.items():
    st.sidebar.markdown(f"## {section}")
    for page in pages:
        # Highlight the active page
        if st.session_state.current_page == page["path"]:
            # Make the active button more prominent
            if st.sidebar.button(f"➤ {page['title']}", key=page["path"],
                                 use_container_width=True,
                                 type="primary"):
                st.session_state.current_page = page["path"]
        else:
            if st.sidebar.button(page["title"], key=page["path"],
                                 use_container_width=True):
                st.session_state.current_page = page["path"]

    # Add some space between sections
    st.sidebar.markdown("---")

# Load and display the selected page
try:
    load_module(st.session_state.current_page)
except Exception as e:
    st.error(f"Error loading page: {e}")