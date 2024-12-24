import streamlit as st
import pandas as pd
import re

# Default match table
default_match_table = {
    "A": "A",
    "mA": "A",
    "U": "U",
    "mU": "U",
    "G": "G",
    "mG": "G",
    "C": "C",
    "mC": "C",
    "D": "U",
}

# Helper function to tokenize input based on match table keys
def tokenize_input(input_string, match_table):
    keys = sorted(match_table.keys(), key=len, reverse=True)  # Sort keys by length to handle multi-char keys
    regex_pattern = "|".join(map(re.escape, keys))
    tokens = re.findall(regex_pattern, input_string)
    return tokens

# Load match table from uploaded file
def load_match_table(file):
    try:
        df = pd.read_csv(file, sep="\t", header=None, names=["key", "value"])
        match_table = dict(zip(df["key"], df["value"]))
        return match_table
    except Exception as e:
        st.error(f"Error loading match table: {e}")
        return None

# Streamlit app
st.title("String Reversal App with Custom Match Table")

st.sidebar.header("Upload Custom Match Table")
file = st.sidebar.file_uploader("Upload a tab-delimited match table (key\tvalue)")

if file:
    match_table = load_match_table(file)
else:
    match_table = default_match_table

st.sidebar.write("Using default match table:", match_table)

st.header("Input String")
#input_string = st.text_area("Enter a string to reverse based on the match table:")
input_sequences = st.text_area("Type or paste the input sequences (one per line)", height=70)
input_sequences = [line.strip() for line in input_sequences.split("\n") if line.strip()]

if st.button("Submit"):
    if not input_sequences:
        st.error("Please enter a string.")
    else:
        res = []
        for input_string in input_sequences:
            tokens = tokenize_input(input_string, match_table)
            if "".join(tokens) != input_string:
                st.error("The input string contains characters not in the match table.")
            else:
                reversed_tokens = [match_table[token] for token in reversed(tokens)]
                output_string = "".join(reversed_tokens)
                res.append(output_string)
            st.success("Reversed String:")
            df = pd.DataFrame(res, columns=["Sequence"])
            st.write(df)


