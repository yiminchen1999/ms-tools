
import numpy as np
import streamlit as st
import pandas as pd
import networkx as nx
import math
import zipfile
import io

def upload_file():
    uploaded_file = st.file_uploader("Choose an Excel file", type="xlsx")
    if uploaded_file:
        df = pd.read_excel(uploaded_file,  dtype={"Charge State Distribution": str})
        df.dropna(inplace=True)
        st.write("Data Preview:", df.head())
        return df
    return None

def upload_mass():
    uploaded_file = st.sidebar.file_uploader("Choose a file", type=["csv", "xlsx", "txt"])
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
        
        return dict(df.values)
    return None

def filter_data(df, mass_cutoff, time_diff_cutoff):
    filtered_df = df[(df["Monoisotopic Mass"] >= mass_cutoff) & 
                     ((df["Stop Time (min)"] - df["Start Time (min)"]) <= time_diff_cutoff)]
    st.write("Filtered Data:", filtered_df)
    return filtered_df

def generate_network(filtered_df, mass_table, similarity_cutoff):
    G = nx.DiGraph()
    masses = filtered_df["Monoisotopic Mass"].tolist()
    mass_intensity = filtered_df[['Monoisotopic Mass', 'Sum Intensity']]
    dict0 = dict(mass_intensity.values) 
    masses = sorted(masses) 
    for i in range(len(masses)):
        m1 = int(masses[i]) 
        for j in range(i + 1, len(masses)):
            mass_diff = abs(masses[j] - masses[i]) 
            for key, value in mass_table.items():
                m2 = int(masses[j])
                if abs(mass_diff - value) < similarity_cutoff:
                    ppm0 =  round((abs(mass_diff - value) / min(m1, m2)) * 1000000, 2)
                    G.add_node(f"M_{m1}")
                    G.add_node(f"M_{m2}")
                    G.add_edge(f"M_{m1}", f"M_{m2}", base=key, ppm=ppm0, intensity1=dict0[masses[i]], intensity2=dict0[masses[j]] ) 
    mass_df = pd.DataFrame({'name':mass_table.keys(), 'mass':mass_table.values()})
    st.write(mass_df) 
    st.write("Network Generated with Nodes and Edges")
    st.write(f"Number of nodes: {G.number_of_nodes()}")
    st.write(f"Number of edges: {G.number_of_edges()}")
    return G

# display and download
def display_edges(G):
    edges = G.edges(data=True)
    edge_list = []
    for edge in edges:
        inten1, inten2 = round(math.log10(edge[2]['intensity1']),2), round(math.log10(edge[2]['intensity2']),2)
        edge_list.append([edge[0], 'massdiff', edge[1], edge[2]['base'],edge[2]['ppm'], inten1, inten2] )
        edges_df = pd.DataFrame(edge_list, columns=["Node1","edge", "Node2", "base", "ppm", 'log-intensity1','log-intensity2'])
    st.write(edges_df)
    return edges_df

@st.cache_data
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(  sep='\t', index=False).encode("utf-8")


# Function to create a zip file from DataFrames
def create_zip_file(df1, df2):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Write df1 to CSV in the zip
        df1_csv = io.StringIO()
        df1.to_csv(df1_csv, sep="\t", index=False)
        zipf.writestr("net.txt", df1_csv.getvalue())

        # Write df2 to CSV in the zip
        df2_csv = io.StringIO()
        df2.to_csv(df2_csv, sep="\t", index=False)
        zipf.writestr("nodes.txt", df2_csv.getvalue())

    buffer.seek(0)
    return buffer


def run_process(df, mass_cutoff, time_diff_cutoff, mass_table, similarity_cutoff):
    filtered_df = filter_data(df, mass_cutoff, time_diff_cutoff)
    with st.spinner('Wait for it...'):
        G = generate_network(filtered_df, mass_table, similarity_cutoff)
        edges = display_edges(G)
#        net = convert_df(edges)
#        st.download_button(label="Download the network",data=csv,file_name="network.txt",mime="text/csv")

        node_intensity1 = edges[['Node1', 'log-intensity1']]
        node_intensity1 = node_intensity1.rename(columns={'Node1': 'Node', 'log-intensity1': 'log-intensity'}) 
        node_intensity2 = edges[["Node2", 'log-intensity2']]
        node_intensity2 = node_intensity2.rename(columns={'Node2': 'Node', 'log-intensity2': 'log-intensity'}) 
        node_intensity = pd.concat([node_intensity1, node_intensity2], ignore_index=True)
        node_intensity = node_intensity.drop_duplicates()
#        nodes = convert_df(node_intensity)

        zip_buffer = create_zip_file(edges,  node_intensity)

    # Provide the download link
        st.download_button(
        label="Download ZIP",
        data=zip_buffer,
        file_name="dataframes.zip",
        mime="application/zip"
    )
#        zip_files_and_download(net, nodes, "network.txt", "node_intensity.txt")
#        st.download_button(label="Download the node-intensity",data=csv1,file_name="node_intensity.txt",mime="text/csv")

# this function is get the combination of two adducts,
# this function eventually not used 
def generate_combine_mass_table(mass_table):
    combine_mass_table = {}
    keys = list(mass_table.keys())

    # Generate all possible combinations of two keys and compute their combined values
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            concatenated_key = keys[i] + "+" + keys[j]
            total_mass = mass_table[keys[i]] + mass_table[keys[j]]
            combine_mass_table[concatenated_key] = total_mass
    combine_mass_table.update(mass_table)
    return combine_mass_table

def round_mass(dict1, decimals=2):
    rounded_dict = {}
    for key, value in dict1.items():
        rounded_dict[key] = np.round(value, decimals=decimals)
    return rounded_dict


def main():
    st.title("Homology Search for Intact RNA")
    mass_table = {'C':305.0413,'A':329.0525,'Oxygen':15.9949,'Me':14.01565,'2Me':28.0313,'Y':358.1599,'Na':22.989769 - 1.00784,'K':39.0983 - 1.00784,'H2O':18.01528,'K-H2O':19.94,'K+Na-2H':59.92,'2Na':43.96,'2K':75.88,'Ph':79.97079, 'CCA':2*305.0413 + 329.0525,'DIPA':101.19-18.01528, '2DIPA': 2*101.19-18.01528} 
    mass_table = round_mass(mass_table)

    df = upload_file()
    if df is not None:
        st.sidebar.header("Filter Options")
        mass_cutoff = st.sidebar.number_input("Monoisotopic Mass Cutoff", min_value=0.0, value=17500.0)
        
        time_diff_cutoff = st.sidebar.number_input("Time Difference Cutoff", min_value=0.0, value=3.0)
        similarity_cutoff = st.sidebar.number_input("Similarity Cutoff for Mass Difference", min_value=0.0, value=0.40)


        st.sidebar.header("Mass Table Options")
        if st.sidebar.button("common isoforms only & generate network"):
#            mass_table = generate_combine_mass_table(mass_table)
            run_process(df, mass_cutoff, time_diff_cutoff, mass_table, similarity_cutoff)

        st.sidebar.header("Add additional mass to Mass search Table")
        new_key = st.sidebar.text_input("New Key")
        new_value = st.sidebar.number_input("New Value", min_value=0.0, value=0.0)
        if st.sidebar.button("Add new mass to Mass Table & generate network"):
            if new_key and new_value:
#                mass_table.update(common_mod)
                mass_table[new_key] = float(new_value)
#                mass_table = generate_combine_mass_table(mass_table)
                mass_table = round_mass(mass_table)
                run_process(df, mass_cutoff, time_diff_cutoff, mass_table, similarity_cutoff)

        st.sidebar.header("upload mass table (header:key,mass) & generate network")
        mass_table = upload_mass() 
        
        if mass_table is not None:
            run_process(df, mass_cutoff, time_diff_cutoff, mass_table, similarity_cutoff)
            # Generate the combined mass table
        

#if __name__ == "__main__":
main()

