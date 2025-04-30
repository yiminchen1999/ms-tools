import streamlit as st
import importlib.util
import sys
import os

# Your current file paths
page_paths = {
    "Info": ["views/about_tools.py"],
    "Data Visualization": ["views/viz_tool/ms_viz_tab.py", "views/viz_tool/fragment_viz.py"],
    "Tools for Intact RNA": ["views/intact_RNA/ms_match_app.py", "views/intact_RNA/homology_search.py"],
    "Tools for Hydrolytic RNA": ["views/hydrolytic_RNA/basecall_net_download5.py", "views/hydrolytic_RNA/st_link_app.py"],
    "Sequence Tools": ["views/seq_tools/seq_aln.py", "views/seq_tools/seq_rev.py"]
}

# Create a dropdown for navigation sections
st.sidebar.title("MS Tools")
section = st.sidebar.selectbox("Choose a section:", list(page_paths.keys()))

# Create a dropdown for pages within the selected section
page_titles = {}
for path in page_paths[section]:
    filename = os.path.basename(path).split('.')[0]
    # Convert snake_case to Title Case
    title = ' '.join(word.capitalize() for word in filename.split('_'))
    page_titles[title] = path

selected_title = st.sidebar.selectbox("Choose a tool:", list(page_titles.keys()))
selected_path = page_titles[selected_title]

# Function to load and run a module from a file path
def import_module_from_path(path):
    module_name = os.path.basename(path).split('.')[0]
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

# Import and run the selected module
try:
    import_module_from_path(selected_path)
except Exception as e:
    st.error(f"Error loading {selected_title}: {e}")