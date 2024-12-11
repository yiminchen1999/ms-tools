
import pandas as pd
import streamlit as st
st.set_page_config(layout="wide") 
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
import networkx as nx

def upload_net():
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "txt"])
    if uploaded_file is not None:
        if uploaded_file.type == "text/csv":
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.type == "application/vnd.ms-excel" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(uploaded_file)
        elif uploaded_file.type == "text/plain":
            df = pd.read_csv(uploaded_file, sep='\t')
        else:
            st.write("Unsupported file type")
            df = None

        return df
    return None

# "Node1","edge", "Node2", "base", "ppm", 'intensity1','intensity2'
def get_nodes(df0):
    node1 = df0[['Node1','log-intensity1']]
    node2 = df0[['Node2','log-intensity2']]
    node1 = node1.rename(columns={'Node1': 'id', 'log-intensity1': 'intensity'})
    node2 = node2.rename(columns={'Node2': 'id', 'log-intensity2': 'intensity'})
    nodes = pd.concat([node1 , node2], axis=0, ignore_index=True)
    nodes = nodes.drop_duplicates()
    nodes['label'] = 'mass'
    nodes_list = nodes.to_dict('records')
    return [{"data": node }  for node in nodes_list]  
   
def get_edges(df0):
    edges = df0[['Node1','Node2','ppm','base']]
    edges = edges.rename(columns={'Node1': 'source', 'Node2': 'target'})
    edges['label'] = 'massdiff'
    edges['id'] = edges['source'] + "-" + edges['target']
    edges_list = edges.to_dict('records')
    return [{"data": edge }  for edge in edges_list]        

def seq_from_node(df0, startnode, cutoff):
    G = nx.DiGraph()
    for index, row in df0.iterrows():
        source, target = row['Node1'], row['Node2']
        attributes = {'base': row['base'], 'ppm': row['ppm'] }
        G.add_edge(source, target, **attributes)
    seq_list, mass_list,ppm_list = [], [], []
    all_paths_from_startnode = []
    for target in G.nodes:
        if startnode != target:
            for path in nx.all_simple_paths(G, source=startnode, target=target):
                if len(path) - 1 >= cutoff:  # Subtract 1 to get the number of edges
                    edge_base, edge_ppm = ["start"], ["ppm"]
                    for i in range(len(path) - 1):
                        u, v = path[i], path[i + 1]
                        edge_attri = G.get_edge_data(u, v)
                        edge_base.append(edge_attri['base'] )
                        edge_ppm.append(str( edge_attri['ppm']) )
                    seq_list.append( '-'.join( edge_base ) )
                    ppm_list.append( '-'.join(edge_ppm )  )
                    mass_list.append('-'.join(path))  
    return seq_list, mass_list, ppm_list


def main():
    df = upload_net()
    if df is not None:
        st.write('Generating network, it will take a while, Wait for it...')
        elements = {"nodes": get_nodes(df), "edges": get_edges(df),}

        # Style node & edge groups
        node_styles = [NodeStyle("mass", "#FF7F3E", "id")]
        edge_styles = [EdgeStyle("massdiff", caption='base', directed=True) ]
#        with st.spinner('Generating network, it will take a while, Wait for it...'):
        st_link_analysis(elements, "cose", node_styles, edge_styles)

        node0  = st.sidebar.text_input("source node")
        cutoff = st.sidebar.number_input("cutoff for seq length", min_value=0, value=3)
        if st.sidebar.button("search all path starting from source node"):
            if node0  and cutoff :
                seq, mass, ppm  = seq_from_node(df, node0, cutoff)
                st.write(seq)
                st.write(mass)
                st.write(ppm)


#if __name__ == "__main__":
#    main()

main()


