import streamlit as st
import importlib.util
import sys
import os


# --- CUSTOM PAGE & NAVIGATION IMPLEMENTATION ---
class CustomPage:
    def __init__(self, path, title=None):
        self.path = path
        self.title = title or os.path.basename(path).replace(".py", "").replace("_", " ").title()

    def run(self):
        # Load and execute the module
        module_name = os.path.basename(self.path).replace(".py", "")
        spec = importlib.util.spec_from_file_location(module_name, self.path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)


# Create a custom navigation function
def custom_navigation(nav_structure):
    # Set up the page configuration
    st.set_page_config(page_title="MS Tools", layout="wide")

    # Initialize session state if needed
    if 'current_section' not in st.session_state:
        st.session_state.current_section = list(nav_structure.keys())[0]
    if 'current_page' not in st.session_state:
        st.session_state.current_page = nav_structure[st.session_state.current_section][0]

    # Display section headers
    for section in nav_structure:
        with st.sidebar:
            st.markdown(f"## {section}")
            for page in nav_structure[section]:
                # Create a button for each page
                if st.button(page.title, key=f"{section}_{page.path}",
                             use_container_width=True,
                             type="primary" if page.path == st.session_state.current_page.path else "secondary"):
                    st.session_state.current_section = section
                    st.session_state.current_page = page
                    st.experimental_rerun()
            st.markdown("---")

    # Return the current page
    return st.session_state.current_page


# --- PAGE SETUP ---
# Create pages using our custom implementation
about_page = CustomPage("views/about_tools.py", title="About tools")
viz_page = CustomPage("views/viz_tool/ms_viz_tab.py", title="MS data plots")
frag_viz_page = CustomPage("views/viz_tool/fragment_viz.py", title="fragment plots")
intact_page = CustomPage("views/intact_RNA/ms_match_app.py", title="mass match")
homology_search = CustomPage("views/intact_RNA/homology_search.py", title="homology search")
net_page = CustomPage("views/hydrolytic_RNA/basecall_net_download5.py", title="net generation")
frag_page = CustomPage("views/hydrolytic_RNA/st_link_app.py", title="find fragments")
seq_aln_page = CustomPage("views/seq_tools/seq_aln.py", title="align sequences")
seq_rev_page = CustomPage("views/seq_tools/seq_rev.py", title="reverse sequences")

# Create navigation structure
nav_structure = {
    "Info": [about_page],
    "Data Visualization": [viz_page, frag_viz_page],
    "Tools for Intact RNA": [intact_page, homology_search],
    "Tools for Hydrolytic RNA": [net_page, frag_page],
    "Sequence Tools": [seq_aln_page, seq_rev_page]
}

# Get the current page from our custom navigation
current_page = custom_navigation(nav_structure)

# Run the selected page
current_page.run()