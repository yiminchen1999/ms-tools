
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go

def upload_file():
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Data Preview:", df.head())
        return df
    return None

def filter_data(df, mass_cutoff, time_diff_cutoff):
    filtered_df = df[(df["Monoisotopic Mass"] >= mass_cutoff) & 
                     ((df["Stop Time (min)"] - df["Start Time (min)"]) <= time_diff_cutoff)]
    st.write("Filtered Data:", filtered_df)
    return filtered_df

def generate_network(filtered_df, mass_table, similarity_cutoff):
    G = nx.DiGraph()
    masses = filtered_df["Monoisotopic Mass"].tolist()
    for i in range(len(masses)):
        m1 = int(masses[i]) 
        for j in range(i + 1, len(masses)):
            mass_diff = abs(masses[j] - masses[i]) 
            for key, value in mass_table.items():
                m2 = int(masses[j])
                if abs(mass_diff - value) < similarity_cutoff:
                    G.add_node(f"M_{m1}")
                    G.add_node(f"M_{m2}")
                    G.add_edge(f"M_{m1}", f"M_{m2}", attribute=key)
    
    st.write("Network Generated with Nodes and Edges")
    st.write(f"Number of nodes: {G.number_of_nodes()}")
    st.write(f"Number of edges: {G.number_of_edges()}")
    return G

# display and download
def display_edges(G):
    edges = G.edges(data=True)
    edge_list = []
    for edge in edges:
        edge_list.append([edge[0], 'massdiff', edge[1], edge[2]['attribute']])
#        st.write(f"Edge: {edge[0]} - {edge[1]}, Property: {edge[2]}")
        edges_df = pd.DataFrame(edge_list, columns=["Node1","edge", "Node2", "Attribute"])
    st.write(edges_df)
    
    return edges_df

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(  sep='\t', index=False).encode("utf-8")

def main():
    st.title("Network Generation and Visualization")
    mass_table = {"C": 305.0413, "U": 306.0254, "A": 329.05, "G": 345.05} # "D":329.04}
    df = upload_file()
    if df is not None:
        st.sidebar.header("Filter Options")
        mass_cutoff = st.sidebar.number_input("Monoisotopic Mass Cutoff", min_value=0.0, value=2500.0)
        time_diff_cutoff = st.sidebar.number_input("Time Difference Cutoff", min_value=0.0, value=3.0)
        similarity_cutoff = st.sidebar.number_input("Similarity Cutoff for Mass Difference", min_value=0.0, value=0.01)

        if st.sidebar.button("Four nucleotides only & generate network"):
            filtered_df = filter_data(df, mass_cutoff, time_diff_cutoff)
            G = generate_network(filtered_df, mass_table, similarity_cutoff)
            edges = display_edges(G)
            csv = convert_df(edges )
            st.download_button(label="Download the network",data=csv,file_name="network.txt",mime="text/csv",)


        st.sidebar.header("Mass Table Options")
        new_key = st.sidebar.text_input("New Key")
        new_value = st.sidebar.number_input("New Value", min_value=0.0, value=0.0)
        if st.sidebar.button("Add new mass to Mass Table & generate network"):
            if new_key and new_value:
                mass_table[new_key] = float(new_value)
                st.sidebar.write("Updated Mass Table:", mass_table)
                filtered_df = filter_data(df, mass_cutoff, time_diff_cutoff)
                G = generate_network(filtered_df, mass_table, similarity_cutoff)
                edges = display_edges(G)
                csv = convert_df(edges)
                st.download_button(label="Download the network",data=csv,file_name="network.txt",mime="text/csv",)


#if __name__ == "__main__":
main()

