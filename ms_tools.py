import streamlit as st

# --- PAGE SETUP ---
about_page = st.Page(page  ='views/about_tools.py',title = "About tools", default = True)

viz_page = st.Page(page = "views/viz_tool/ms_viz_tab.py",title = "MS data plots" )
frag_viz_page= st.Page(page = "views/viz_tool/fragment_viz.py", title = "fragment plots" )

intact_page = st.Page(page = "views/intact_RNA/ms_match_app.py", title = "mass match")
homology_search = st.Page(page = "views/intact_RNA/homology_search.py", title = "homology search")

net_page = st.Page(page = "views/hydrolytic_RNA/basecall_net_download5.py", title = "net generation")
frag_page = st.Page(page = "views/hydrolytic_RNA/st_link_app.py", title = "find fragments")

seq_aln_page = st.Page(page = "views/seq_tools/seq_aln.py", title = "align sequences")
seq_rev_page = st.Page(page = "views/seq_tools/seq_rev.py", title = "reverse sequences")

pg = st.navigation( 
    { "Info":  [about_page], 
      "Data Visualization": [viz_page, frag_viz_page],
      "Tools for Intact RNA":[intact_page, homology_search], 
      "Tools for Hydrolytic RNA" :[net_page, frag_page],
      "Sequence Tools": [seq_aln_page, seq_rev_page],
})

pg.run()

