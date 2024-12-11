import streamlit as st
import pandas as pd
st.set_page_config(layout='wide')

# Helper functions
def load_text_file(file):
    """Load content from a text file."""
    return file.read().decode("utf-8")

def parse_match_table(file_content):
    """Parse match table from a text file."""
    match_table = {}
    for line in file_content.strip().split("\n"):
        key, value = line.strip().split()
        match_table[key] = value
    return match_table

def tokenize_sequence(sequence, match_table):
    """Tokenize a sequence based on match table keys."""
    tokens = []
    i = 0
    while i < len(sequence):
        if i + 1 < len(sequence) and sequence[i:i+2] in match_table:
            tokens.append(sequence[i:i+2])
            i += 2
        elif sequence[i] in match_table:
            tokens.append(sequence[i])
            i += 1
        else:
            raise ValueError(f"Invalid sequence element: {sequence[i]} at position {i}")
    return tokens

def find_alignment(reference, sequences, match_table, max_mismatches):
    """Align sequences to the reference based on the match table and mismatch cutoff."""
    ref_tokens = tokenize_sequence(reference, match_table)
    ref_values = [match_table[token] for token in ref_tokens]
    all_aligned_sequences = []

    for seq in sequences:
        seq_tokens = tokenize_sequence(seq, match_table)
        seq_values = [match_table[token] for token in seq_tokens]
        rev_seq_tokens = seq_tokens[::-1]
        rev_seq_values = seq_values[::-1]

        for seq_variant, seq_variant_values, label in [
            (seq_tokens, seq_values, "Original"),
            (rev_seq_tokens, rev_seq_values, "Reversed"),
        ]:
            for start in range(len(ref_values) - len(seq_variant_values) + 1):
                mismatch_count = sum(
                    1 for i in range(len(seq_variant_values)) if ref_values[start + i] != seq_variant_values[i]
                )
                if mismatch_count <= max_mismatches:
                    aligned_seq = " " * start + "".join(seq_variant_values) + " " * (
                        len(ref_values) - start - len(seq_variant_values)
                    )
                    all_aligned_sequences.append((aligned_seq, label, start, seq_variant))

    return all_aligned_sequences

def generate_alignment_display(reference, alignments, match_table):
    """Generate a visual alignment of reference and input sequences."""
    ref_tokens = tokenize_sequence(reference, match_table)
    ref_values = [match_table[token] for token in ref_tokens]
    display = ["".join(ref_values)]  # Add reference values as the first line

    for aligned_seq, label, position, seq_tokens in alignments:
        aligned_values = "".join([match_table[token] for token in seq_tokens])
        alignment_line = " " * position + aligned_values
        display.append(f"{alignment_line} [{label}, Position: {position}]")
    return "\n".join(display)  # Combine all lines into a single block

# Streamlit UI
st.title("Sequence Alignment Tool")

# Sidebar for inputs
st.sidebar.header("Input Parameters")

# Reference sequence input grouped in one container
with st.sidebar.container():
    st.subheader("Reference Sequence")
    reference = st.text_area("Type or paste the reference sequence below", height=70)
#    uploaded_ref_file = st.file_uploader("Or upload a reference sequence file", type=["txt"])
#    if uploaded_ref_file:
#        reference = load_text_file(uploaded_ref_file)

# Input sequences grouped in another container
with st.sidebar.container():
    st.subheader("Input Sequences")
    input_sequences = st.text_area("Type or paste the input sequences (one per line)", height=70)
#    uploaded_input_file = st.file_uploader("Or upload an input sequences file", type=["txt"])
#    if uploaded_input_file:
#        input_sequences = load_text_file(uploaded_input_file)

# Mismatch cutoff
max_mismatches = st.sidebar.number_input("Maximum Allowed Mismatches", min_value=0, value=0, step=1)

# Match table
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
uploaded_match_file = st.sidebar.file_uploader("Upload Match Table", type=["txt"])
if uploaded_match_file:
    match_table = parse_match_table(load_text_file(uploaded_match_file))
else:
    match_table = default_match_table
match_table["original"] = "value"
matchtable_df = pd.DataFrame.from_dict([ match_table] )
matchtable_df.set_index('original', inplace=True)
st.header("match table used for alignment" )
st.write(matchtable_df)


# Submit button
if st.sidebar.button("Submit"):
    if not reference or not input_sequences:
        st.error("Please provide both a reference sequence and input sequences.")
    else:
        try:
            # Process input sequences
            input_sequences = [line.strip() for line in input_sequences.split("\n") if line.strip()]

            # Find alignments
            alignments = find_alignment(reference, input_sequences, match_table, max_mismatches)

            if alignments:
                st.subheader("Alignment Results")
                alignment_display = generate_alignment_display(reference, alignments, match_table)
                st.code(alignment_display)  # Display all lines in the same block
            else:
                st.info("No alignments found within the specified mismatch threshold.")
        except ValueError as e:
            st.error(str(e)) 



