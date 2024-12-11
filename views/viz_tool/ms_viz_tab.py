import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import math

st.set_page_config(layout="wide") 

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


# Main function to run the Streamlit app

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
            zaxis_title='RT'),
            title_x=0.3
        )
        fig.update_traces(marker=dict(size=2))

        # Enable full screen mode
        config = {'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['fullScreen']}

        # Display the Plotly figure in Streamlit
        st.plotly_chart(fig, use_container_width=True, config=config)
    else:
        st.write("The uploaded file does not contain the required columns: Mass, Intensity, and RT.")

# Function to creat and display 2-d scatter plot
def plot_2d_scatter(df, mass_range, intensity_range, rt_range, yaxis):
    required_columns = ['Mass', 'Intensity', 'RT']
    if all(column in df.columns for column in required_columns):
        # Filter the DataFrame based on the selected ranges
        filtered_df = df[
            (df['Mass'] >= mass_range[0]) & (df['Mass'] <= mass_range[1]) &
            (df['Intensity'] >= intensity_range[0]) & (df['Intensity'] <= intensity_range[1]) &
            (df['RT'] >= rt_range[0]) & (df['RT'] <= rt_range[1])
        ]

        if yaxis == "Intensity":
            fig = px.scatter(filtered_df, x='Mass', y='Intensity', title='Mass vs Intensity(log)')
            fig.update_layout(scene=dict(xaxis_title='Mass',yaxis_title='Intensity(log10)'))
        if yaxis == "RT":
            fig = px.scatter(filtered_df, x='Mass', y='RT', title='Mass vs RT')
            fig.update_layout(scene=dict(xaxis_title='Mass',yaxis_title='Retentation Time'))
        fig.update_traces(marker=dict(size=2))

        # Enable full screen mode
        config = {'displayModeBar': True, 'scrollZoom': True, 'displaylogo': False, 'modeBarButtonsToAdd': ['fullScreen']}
#        return fig
        # Display the Plotly figure in Streamlit
        st.plotly_chart(fig, use_container_width=True, config=config)
    else:
        st.write("The uploaded file does not contain the required columns: Mass, Intensity, and RT.")

def tab_scatter(df, mass_range, intensity_range, rt_range, stop_start_cutoff):
    # Title of the Streamlit app
    st.title("Mass-Intensity-RT Scatter Plot")

    if df is not None:
        df = df[(df['Stop Time (min)'] - df['Start Time (min)']) <= stop_start_cutoff]
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            plot_2d_scatter(df, mass_range, intensity_range, rt_range, "RT")
        # Plot the 3D scatter plot if DataFrame is valid
        with col2:
            plot_3d_scatter(df, mass_range, intensity_range, rt_range)

        with col3:
            plot_2d_scatter(df, mass_range, intensity_range, rt_range, "Intensity")


# Function to compute the outer subtraction of Mass and its self
@st.cache_data
def compute_mass_diff(df, arg1=100, arg2=1000):
    mass_values = df['Mass'].values
    mass_diff = np.subtract.outer(mass_values, mass_values)
    
    # Filter the mass differences to keep only those within the range [arg1, arg2]
    mass_diff = mass_diff[(mass_diff >= arg1) & (mass_diff <= arg2)]
    
    # Convert the filtered array to a DataFrame
    #mass_diff = pd.DataFrame(mass_diff, columns=df['Mass'], index=df['Mass'])
    
    return mass_diff

# Function to create and display the histogram of mass_diff
def plot_mass_diff_histogram(mass_diff, hist_range, add_lines, user_defined_value=None):
    # Flatten the DataFrame and filter for positive values
    #positive_mass_diff = mass_diff.values[mass_diff.values > 0]
    hist_range = st.slider("Select Histogram Range", hist_range[0], hist_range[1], (hist_range[0], hist_range[1]))
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
        
        fig.add_vline(x=user_defined_value, line_dash="dash", line_color="orange")
    
    # Display the Plotly figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)
    
    


# Main function to run the Streamlit app
def tab_hstogram(df, mass_range, intensity_range, rt_range, stop_start_cutoff):
    # Title of the Streamlit app
    st.title("Mass Difference Histogram")

    if df is not None:
        df = df[(df['Stop Time (min)'] - df['Start Time (min)']) <= stop_start_cutoff]
        # filtering data
        df = filter_data(df, mass_range, intensity_range, rt_range)

        # Compute the outer subtraction of Mass and its self
        with st.spinner("please waiting"):
           mass_diff = compute_mass_diff(df)

        col1, col2, col3 = st.columns(3)

        # Create checkboxes for adding vertical lines
        st.header("Add Vertical Lines")
        add_lines = {
            '305': st.checkbox("Add Line at 305 (C)"),
            '306': st.checkbox("Add Line at 306 (U)"),
            '329': st.checkbox("Add Line at 329 (A)"),
            '345': st.checkbox("Add Line at 345 (G)"),
            'user_defined': st.checkbox("Add User-Defined Line")
        }
        user_defined_value = st.number_input("Enter User-Defined Value", value=0.0)

        # Plot the histogram of mass_diff
        with col1, st.spinner("please waiting"):
            plot_mass_diff_histogram(mass_diff, [300,360], add_lines,user_defined_value)

        with col2, st.spinner("please waiting")  :
            plot_mass_diff_histogram(mass_diff, [600,750], add_lines,user_defined_value)

        with col3, st.spinner("please waiting"):
            # Create a slider for the histogram range
            plot_mass_diff_histogram(mass_diff, [0,1000], add_lines, user_defined_value)


# Function to create and display the 3D scatter plot
def filter_data(df, mass_range, intensity_range, rt_range):
    required_columns = ['Mass', 'Intensity', 'RT']
    if all(column in df.columns for column in required_columns):
        # Filter the DataFrame based on the selected ranges
        filtered_df = df[
            (df['Mass'] >= mass_range[0]) & (df['Mass'] <= mass_range[1]) &
            (df['Intensity'] >= intensity_range[0]) & (df['Intensity'] <= intensity_range[1]) &
            (df['RT'] >= rt_range[0]) & (df['RT'] <= rt_range[1])
        ]

    return filtered_df


st.header("MS data visualization tool")
st.subheader("Scatter plots of Mass, Intensity and Rentation Time")
st.text("Upload the file after deconvulution, three scatter plots will be created.")

df = upload_file()
if df is not None:
    # Get the min and max values for the sliders
    mass_min, mass_max = float(df['Mass'].min()), float(df['Mass'].max())
    intensity_min, intensity_max = float(df['Intensity'].min()), float(df['Intensity'].max())
    rt_min, rt_max = float(df['RT'].min()), float(df['RT'].max())

    # Create sliders for Mass, Intensity, and RT

    st.sidebar.header("Filter Data")
    stop_start_cutoff = st.sidebar.number_input("'Stop Time (min)' - 'Start Time (min)':", value= 5)
    mass_range = st.sidebar.slider("Select Mass Range", mass_min, mass_max, (mass_min, mass_max))
    intensity_range = st.sidebar.slider("Select Intensity Range", intensity_min, intensity_max, (intensity_min, intensity_max))
    rt_range = st.sidebar.slider("Select RT Range", rt_min, rt_max, (rt_min, rt_max))

    tab1, tab2 = st.tabs(["Scatter plot", "histogram"])

    with tab1:
        tab_scatter(df, mass_range, intensity_range, rt_range, stop_start_cutoff)

    with tab2:
        tab_hstogram(df, mass_range, intensity_range, rt_range, stop_start_cutoff)


# Run the app with: streamlit run your_script.py
#if __name__ == "__main__":
#main()
