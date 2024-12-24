
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
st.set_page_config(layout="wide") 

# Function to process the input files
def process_files(df, df_nets):
    extracted_rows = []
    annotations_3d = []

    # Process each net and base
    for i, row in df_nets.iterrows():
        net = row["nets"]
        base = row["bases"]

        # Split net and base
        path = net.split("-")
        bases_path = base.split("-")

        # Ensure paths and bases match
        if len(path) != len(bases_path):
            raise ValueError(f"Mismatch between 'nets' and 'bases' for row {i + 1}.")

        # Process each node in the path
        for node, base in zip(path, bases_path):
            rows = df[df["NodeName"] == node].copy()
            rows["Net Source"] = f"Net {i + 1}"  # Add net source
            rows["Base"] = base  # Add base annotation
            rows["Group"] = f"Group {i + 1}"  # Group identifier
            extracted_rows.append(rows)

            # Prepare annotations for the 3D plot
            if not rows.empty:
                annotations_3d.append({
                    "Monoisotopic Mass": rows.iloc[0]["Monoisotopic Mass"],
                    "Sum Intensity": rows.iloc[0]["Sum Intensity"],
                    "Apex RT": rows.iloc[0]["Apex RT"],
                    "Base": base,
                    "Group": f"Group {i + 1}",
                })

    # Combine extracted rows into a single DataFrame
    if extracted_rows:
        extracted_df = pd.concat(extracted_rows, ignore_index=True)
        return extracted_df, annotations_3d
    else:
        raise ValueError("No matching rows found for the given nets paths.")

# Function to create 3D plot
def create_3d_plot(extracted_df, annotations_3d):
    fig = go.Figure()

    # Add data points grouped by Group
    for group_name in extracted_df["Group"].unique():
        group_data = extracted_df[extracted_df["Group"] == group_name]

        fig.add_trace(
            go.Scatter3d(
                x=group_data["Monoisotopic Mass"],
                y=group_data["Sum Intensity"],
                z=group_data["Apex RT"],
                mode="markers+text",
                text=group_data["Base"],
                textposition="top center",
                name=group_name,
                marker=dict(size=5),
            )
        )

    # Update layout
    fig.update_layout(
        title="3D Scatter Plot",
        scene=dict(
            xaxis_title="Monoisotopic Mass",
            yaxis_title="Sum Intensity",
            zaxis_title="Apex RT",
        ),
        showlegend=True,
    )

    return fig

# Function to create 2D plot with grouped coloring
def create_2d_grouped_plot(extracted_df, x_column, y_column, x_label, y_label, title):
    fig = go.Figure()

    # Add data points grouped by Group
    for group_name in extracted_df["Group"].unique():
        group_data = extracted_df[extracted_df["Group"] == group_name]

        fig.add_trace(
            go.Scatter(
                x=group_data[x_column],
                y=group_data[y_column],
                mode="markers",
                name=group_name,
                marker=dict(size=6),
            )
        )

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        showlegend=True,
    )

    return fig

# Main Streamlit app function
def main():
    st.header("MS data visualization tool")
    st.subheader("Scatter plots of Mass, Intensity and Rentation Time for identified fragments")
    st.text("Upload the file after deconvulution and fragments, three scatter plots will be created.")

    # Sidebar for file uploaders
    st.header("Upload Files")

    # File uploader for the first file
    file1 = st.file_uploader("Upload deconvlution results", type=["txt", "csv", "xlsx"])

    # File uploader for the second file
    file2 = st.file_uploader("Upload excel file with fragments (with 'nets' and 'bases' columns)", type=["xlsx"])

    if st.button("Submit"):
        if file1 and file2:
            # Read the first file into a DataFrame
            if file1.name.endswith("xlsx"):
                df = pd.read_excel(file1)
            else:
                df = pd.read_csv(file1, delimiter=None)  # Handles both txt and csv
            df = df.dropna(subset=["Monoisotopic Mass", "Sum Intensity", "Apex RT"])

            # Ensure required columns exist
            if not all(col in df.columns for col in ["Monoisotopic Mass", "Sum Intensity", "Apex RT"]):
                st.error("The first file must contain 'Monoisotopic Mass', 'Sum Intensity', and 'Apex RT' columns.")
                return

            # Create "NodeName" column
            df["NodeName"] = "M_" + df["Monoisotopic Mass"].astype(int).astype(str)

            # Read the second file into a DataFrame
            if file2.name.endswith("xlsx"):
                df_nets = pd.read_excel(file2)
            else:
                df_nets = pd.read_csv(file2, delimiter=None)

            # Ensure required columns exist in the second file
            if not all(col in df_nets.columns for col in ["nets", "bases"]):
                st.error("The second file must contain 'nets' and 'bases' columns.")
                return

            try:
                # Process files and extract data
                extracted_df, annotations_3d = process_files(df, df_nets)
                st.write(extracted_df)

                # Create plots
                col1, col2, col3 = st.columns(3)

                with col1:
#                    st.subheader("Mass vs Apex RT")
                    fig_2d_1 = create_2d_grouped_plot(
                        extracted_df,
                        "Monoisotopic Mass",
                        "Apex RT",
                        x_label="Monoisotopic Mass",
                        y_label="Apex RT",
                        title="Mass vs Apex RT"
                    )
                    st.plotly_chart(fig_2d_1, use_container_width=True)

                with col2:
#                    st.subheader("3D Scatter Plot")
                    fig_3d = create_3d_plot(extracted_df, annotations_3d)
                    st.plotly_chart(fig_3d, use_container_width=True)

                with col3:
#                    st.subheader("Mass vs Sum Intensity")
                    fig_2d_2 = create_2d_grouped_plot(
                        extracted_df,
                        "Monoisotopic Mass",
                        "Sum Intensity",
                        x_label="Monoisotopic Mass",
                        y_label="Sum Intensity",
                        title="Mass vs Sum Intensity"
                    )
                    st.plotly_chart(fig_2d_2, use_container_width=True)

            except ValueError as e:
                st.error(str(e))
        else:
            st.error("Please upload both files before submitting.")

#if __name__ == "__main__":
main()

