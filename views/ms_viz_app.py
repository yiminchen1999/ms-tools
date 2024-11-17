import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math

# Function to upload and read the file
def upload_file():
    uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "txt", "tab", "xls"])
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
        df = df.dropna()
        df["Intensity"] = df['Sum Intensity'].astype('int64') 
        df['logIntentsity'] = np.log10(df['Intensity'])
        df['Intensity'] = df['logIntentsity']
        df["Mass"] = df["Monoisotopic Mass"]
        df["RT"] = df["Apex RT"]

        return df
    return None

# Function to compute the outer subtraction of Mass and its self
def compute_mass_diff(df, arg1=280, arg2=400):
    mass_values = df['Mass'].values
    mass_diff = np.subtract.outer(mass_values, mass_values)
    
    # Filter the mass differences to keep only those within the range [arg1, arg2]
    mass_diff = mass_diff[(mass_diff >= arg1) & (mass_diff <= arg2)]
    
    # Convert the filtered array to a DataFrame
    #mass_diff = pd.DataFrame(mass_diff, columns=df['Mass'], index=df['Mass'])
    
    return mass_diff

# Function to create and display the histogram of mass_diff
def plot_mass_diff_histogram(mass_diff, hist_range, add_lines):
    # Flatten the DataFrame and filter for positive values
    #positive_mass_diff = mass_diff.values[mass_diff.values > 0]
    
    # Create a histogram using Plotly
    bin_width= 50
    nbins = math.ceil(max(mass_diff) - min(mass_diff) / bin_width)

    fig = px.histogram(mass_diff, nbins=nbins, range_x=hist_range, title='Histogram of Positive Mass Differences')
    
    # Update layout for better visualization
    fig.update_layout(xaxis_title='Mass Difference', yaxis_title='Frequency')
    
    # Add vertical lines if checkboxes are selected
    if add_lines['305']:
        fig.add_vline(x=305, line_dash="dash", line_color="green")
    if add_lines['306']:
        fig.add_vline(x=306, line_dash="dash", line_color="blue")
    if add_lines['329']:
        fig.add_vline(x=329, line_dash="dash", line_color="red")
    if add_lines['345']:
        fig.add_vline(x=345, line_dash="dash", line_color="purple")
    if add_lines['user_defined']:
        user_defined_value = st.sidebar.number_input("Enter User-Defined Value", value=0.0)
        fig.add_vline(x=user_defined_value, line_dash="dash", line_color="orange")
    
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

# Main function to run the Streamlit app
def main():
    # Title of the Streamlit app
    st.title("Mass-Intensity-RT Scatter Plot and Mass Difference Histogram")

    # Upload the file and get the DataFrame
    df = upload_file()

    if df is not None:
        # Get the min and max values for the sliders
        mass_min, mass_max = float(df['Mass'].min()), float(df['Mass'].max())
        intensity_min, intensity_max = float(df['Intensity'].min()), float(df['Intensity'].max())
        rt_min, rt_max = float(df['RT'].min()), float(df['RT'].max())

        # Create sliders for Mass, Intensity, and RT
        st.sidebar.header("Filter Data")
        mass_range = st.sidebar.slider("Select Mass Range", mass_min, mass_max, (mass_min, mass_max))
        intensity_range = st.sidebar.slider("Select Intensity Range", intensity_min, intensity_max, (intensity_min, intensity_max))
        rt_range = st.sidebar.slider("Select RT Range", rt_min, rt_max, (rt_min, rt_max))

        # Plot the 3D scatter plot if DataFrame is valid
        plot_3d_scatter(df, mass_range, intensity_range, rt_range)

        # Compute the outer subtraction of Mass and its self
        mass_diff = compute_mass_diff(df)

        # Get the min and max values for the histogram slider
        min_mass_diff = min(mass_diff) #.values[mass_diff.values > 0].min()
        max_mass_diff = max(mass_diff) #.values[mass_diff.values > 0].max()

        # Create a slider for the histogram range
        hist_range = st.sidebar.slider("Select Histogram Range", min_mass_diff, max_mass_diff, (min_mass_diff, max_mass_diff))

        # Create checkboxes for adding vertical lines
        st.sidebar.header("Add Vertical Lines")
        add_lines = {
            '305': st.sidebar.checkbox("Add Line at 305"),
            '306': st.sidebar.checkbox("Add Line at 306"),
            '329': st.sidebar.checkbox("Add Line at 329"),
            '345': st.sidebar.checkbox("Add Line at 345"),
            'user_defined': st.sidebar.checkbox("Add User-Defined Line")
        }

        # Plot the histogram of mass_diff
        plot_mass_diff_histogram(mass_diff, hist_range, add_lines)

# Function to create and display the 3D scatter plot
def plot_3d_scatter(df, mass_range, intensity_range, rt_range):
    required_columns = ['Mass', 'Intensity', 'RT']
    if all(column in df.columns for column in required_columns):
        # Filter the DataFrame based on the selected ranges
        filtered_df = df[
            (df['Mass'] >= mass_range[0]) & (df['Mass'] <= mass_range[1]) &
            (df['Intensity'] >= intensity_range[0]) & (df['Intensity'] <= intensity_range[1]) &
            (df['RT'] >= rt_range[0]) & (df['RT'] <= rt_range[1])
        ]

        # Create a 3D scatter plot using Plotly
        fig = px.scatter_3d(filtered_df, x='Mass', y='Intensity', z='RT',
                            title='3D Scatter Plot of Mass, Intensity(log10), and RT')

        # Update layout for better visualization
        fig.update_layout(scene=dict(
            xaxis_title='Mass',
            yaxis_title='Intensity(log10)',
            zaxis_title='RT'
        ))
        fig.update_traces(marker=dict(size=2))

        # Enable full screen mode
        config = {'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['fullScreen']}

        # Display the Plotly figure in Streamlit
        st.plotly_chart(fig, use_container_width=True, config=config)
    else:
        st.write("The uploaded file does not contain the required columns: Mass, Intensity, and RT.")

# Run the app with: streamlit run your_script.py
#if __name__ == "__main__":
main()
