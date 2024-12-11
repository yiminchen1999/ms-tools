
import streamlit as st
import pandas as pd

# Function to process the first Excel file
def process_first_file(file, stop_start_cutoff, monoisotopic_mass_cutoff):
    df = pd.read_excel(file)
    # Remove rows where the difference between "Stop Time (min)" and "Start Time (min)" is larger than the specified cutoff
    df = df[(df['Stop Time (min)'] - df['Start Time (min)']) <= stop_start_cutoff]
    # Remove rows where "Monoisotopic Mass" is smaller than the specified cutoff
    df = df[df['Monoisotopic Mass'] >= monoisotopic_mass_cutoff]
    return df

# Function to process the second Excel file and find matches
def process_second_file(file, first_df, matched_criterion):
    df = pd.read_excel(file)
    mass_columns = ["Mass_CCA", "Mass_CC", "Mass_C", "Mass_AA"]
    matched_rows = pd.DataFrame()

    for index, row in first_df.iterrows():
        monoisotopic_mass = row['Monoisotopic Mass']
        sum_intensity = row['Sum Intensity']
        relative_abundance = row['Relative Abundance']

        for mass_col in mass_columns:
            matched_rows_temp = df[abs(df[mass_col] - monoisotopic_mass)  < matched_criterion ]
            if not matched_rows_temp.empty:
                matched_rows_temp['Matching_Mass_Column'] = mass_col
                matched_rows_temp['Monoisotopic Mass'] = monoisotopic_mass
                matched_rows_temp['Sum Intensity'] = sum_intensity
                matched_rows_temp['Relative Abundance'] = relative_abundance
                matched_rows = pd.concat([matched_rows, matched_rows_temp], ignore_index=True)

    return matched_rows

# Streamlit app
st.title("Tools for Intact RNA Mass")
st.header("Mass Matcher with Database")
st.text("upload two files, the results from deconvolution and the database file, four masses(Mass_C, Mass_CC, Mass_CCA and Mass_AA) from database will be compared with the one from experiment" )

# Initialize session state
if 'first_file_processed' not in st.session_state:
    st.session_state.first_file_processed = False
if 'second_file_processed' not in st.session_state:
    st.session_state.second_file_processed = False

# File upload for the first Excel file
st.subheader("Upload the output file from deconvolution")
first_file = st.file_uploader("Choose a file", type="xlsx", key="first_file_uploader")

if first_file is not None:
    stop_start_cutoff = st.number_input("Enter the cutoff for the difference between 'Stop Time (min)' and 'Start Time (min)':", value= 5)
    monoisotopic_mass_cutoff = st.number_input("Enter the cutoff for 'Monoisotopic Mass':", value=20000)
    first_df = process_first_file(first_file, stop_start_cutoff, monoisotopic_mass_cutoff)
    st.session_state.first_file_processed = True
    st.write("First file processed successfully.")

# File upload for the second Excel file
st.subheader("Upload the tRNA database file (tRNA_DB_human.xlsx)")
second_file = st.file_uploader("Choose a file", type="xlsx", key="second_file_uploader")

if second_file is not None:
    matched_criterion = st.number_input("Enter the matched criterion (absolute difference between 'Monoisotopic Mass' and theoretical mass):", value= 0.25)
    matched_rows = process_second_file(second_file, first_df, matched_criterion)
    st.session_state.second_file_processed = True
    st.write("Second file processed successfully.")

# Button to display matched rows
if st.session_state.first_file_processed and st.session_state.second_file_processed:
    if st.button("Display Match"):
        st.subheader("Matched Rows")
        st.write(matched_rows)
else:
    st.write("Please upload and process both files to display the matched rows.")
