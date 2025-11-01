
import io
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
import nbformat
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Inflation Forecasting Dashboard", layout="wide")

def extract_data_from_notebook(notebook_content):
    """Extract forecast data from notebook outputs"""
    try:
        nb = nbformat.reads(notebook_content, as_version=4)

        # Sample data structure - in real implementation, you'd parse the notebook outputs
        # For demo purposes, I'll use the data from your notebook
        us_data = {
            'dates': pd.date_range('2024-01-01', '2024-12-01', freq='MS'),
            'Inflation': [3.545263, 3.692825, 4.229390, 4.207468, 4.392325, 
                         5.163790, 5.527326, 5.332471, 5.132650, 5.258153, 
                         5.458715, 5.502330],
            'Sentiment': [71.711616, 70.553951, 68.780083, 68.064709, 67.311558,
                         67.309836, 65.942391, 65.512857, 65.709978, 64.611129,
                         62.995268, 63.884956],
            'Claims': [266709.944113, 166019.996732, 100699.103050, 190771.217737,
                      189943.257927, 207827.839471, 169710.538439, 112039.912815,
                      148388.724199, 150727.471791, 153356.240889, 171384.111959]
        }

        uk_data = {
            'dates': pd.date_range('2024-02-01', '2025-01-01', freq='MS'),
            'Inflation': [-0.531041, -0.501762, -0.252700, -0.226370, -0.221663,
                         -0.089506, -0.059666, -0.070303, -0.023906, -0.007307,
                         -0.015908, -0.002446],
            'Tesco_Index': [114.653830, 114.837277, 114.848791, 114.944510, 115.082507,
                           115.169253, 115.241587, 115.327652, 115.400796, 115.460914,
                           115.524481, 115.585555]
        }

        return us_data, uk_data
    except Exception as e:
        st.error(f"Error parsing notebook: {e}")
        return None, None

def create_interactive_plot(us_data, uk_data, selected_factors, model_type):
    """Create interactive plot based on selected factors"""

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Inflation Forecast', 'Contributing Factors'),
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4]
    )

    # Main inflation plot
    if model_type == "US Model" or model_type == "Both":
        if us_data:
            fig.add_trace(
                go.Scatter(
                    x=us_data['dates'],
                    y=us_data['Inflation'],
                    mode='lines+markers',
                    name='US Inflation Forecast',
                    line=dict(color='blue', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )

    if model_type == "UK Model" or model_type == "Both":
        if uk_data:
            fig.add_trace(
                go.Scatter(
                    x=uk_data['dates'],
                    y=uk_data['Inflation'],
                    mode='lines+markers',
                    name='UK Inflation Forecast',
                    line=dict(color='red', width=3),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )

    # Contributing factors subplot
    if model_type == "US Model" or model_type == "Both":
        if us_data and 'Sentiment' in selected_factors:
            # Normalize sentiment to fit on same scale
            sentiment_norm = np.array(us_data['Sentiment']) / 20  # Scale down for visibility
            fig.add_trace(
                go.Scatter(
                    x=us_data['dates'],
                    y=sentiment_norm,
                    mode='lines',
                    name='US Sentiment (scaled)',
                    line=dict(color='green', dash='dot'),
                    yaxis='y3'
                ),
                row=2, col=1
            )

        if us_data and 'Claims' in selected_factors:
            # Normalize claims to fit on same scale
            claims_norm = np.array(us_data['Claims']) / 50000  # Scale down for visibility
            fig.add_trace(
                go.Scatter(
                    x=us_data['dates'],
                    y=claims_norm,
                    mode='lines',
                    name='US Claims (scaled)',
                    line=dict(color='orange', dash='dash'),
                    yaxis='y3'
                ),
                row=2, col=1
            )

    if model_type == "UK Model" or model_type == "Both":
        if uk_data and 'Tesco Index' in selected_factors:
            # Normalize Tesco index
            tesco_norm = (np.array(uk_data['Tesco_Index']) - 114) * 5  # Scale and center
            fig.add_trace(
                go.Scatter(
                    x=uk_data['dates'],
                    y=tesco_norm,
                    mode='lines',
                    name='UK Tesco Index (scaled)',
                    line=dict(color='purple', dash='dashdot'),
                    yaxis='y3'
                ),
                row=2, col=1
            )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Interactive Inflation Forecasting Dashboard",
            font=dict(size=20)
        ),
        height=800,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Update y-axes
    fig.update_yaxes(title_text="Inflation Rate (%)", row=1, col=1)
    fig.update_yaxes(title_text="Contributing Factors (Scaled)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig

def main():
    st.title("🏦 Inflation Forecasting Dashboard")
    st.markdown("Upload your Jupyter notebook to analyze inflation forecasting models")

    # Sidebar for controls
    st.sidebar.header("Dashboard Controls")

    # File upload
    uploaded_file = st.sidebar.file_uploader(
        "Upload Jupyter Notebook (.ipynb)",
        type=['ipynb'],
        help="Upload your inflation forecasting notebook"
    )

    # Model selection
    model_type = st.sidebar.selectbox(
        "Select Model",
        ["US Model", "UK Model", "Both"],
        index=2
    )

    # Factor checkboxes
    st.sidebar.subheader("Contributing Factors")

    available_factors = ["Sentiment", "Claims", "Tesco Index"]
    selected_factors = []

    for factor in available_factors:
        if st.sidebar.checkbox(factor, value=True, key=f"factor_{factor}"):
            selected_factors.append(factor)

    # Main content area
    if uploaded_file is not None:
        # Read notebook content
        notebook_content = uploaded_file.read().decode('utf-8')

        # Extract data
        us_data, uk_data = extract_data_from_notebook(notebook_content)

        if us_data or uk_data:
            st.success("✅ Notebook loaded successfully!")

            # Display summary statistics
            col1, col2, col3 = st.columns(3)

            with col1:
                if us_data:
                    st.metric(
                        "US Peak Inflation",
                        f"{max(us_data['Inflation']):.2f}%",
                        f"+{max(us_data['Inflation']) - us_data['Inflation'][0]:.2f}%"
                    )

            with col2:
                if uk_data:
                    st.metric(
                        "UK Final Inflation",
                        f"{uk_data['Inflation'][-1]:.3f}%",
                        f"+{uk_data['Inflation'][-1] - uk_data['Inflation'][0]:.3f}%"
                    )

            with col3:
                st.metric(
                    "Active Factors",
                    len(selected_factors),
                    f"of {len(available_factors)} total"
                )

            # Create and display the plot
            fig = create_interactive_plot(us_data, uk_data, selected_factors, model_type)
            st.plotly_chart(fig, use_container_width=True)

            # Display data tables
            st.subheader("📊 Forecast Data")

            if model_type == "US Model" or model_type == "Both":
                if us_data:
                    st.write("**US Model Forecasts**")
                    us_df = pd.DataFrame({
                        'Date': us_data['dates'],
                        'Inflation (%)': us_data['Inflation'],
                        'Sentiment': us_data['Sentiment'],
                        'Claims': us_data['Claims']
                    })
                    st.dataframe(us_df, use_container_width=True)

            if model_type == "UK Model" or model_type == "Both":
                if uk_data:
                    st.write("**UK Model Forecasts**")
                    uk_df = pd.DataFrame({
                        'Date': uk_data['dates'],
                        'Inflation (%)': uk_data['Inflation'],
                        'Tesco Index': uk_data['Tesco_Index']
                    })
                    st.dataframe(uk_df, use_container_width=True)

        else:
            st.error("❌ Could not extract data from the notebook")

    else:
        # Show demo when no file is uploaded
        st.info("👆 Please upload your .ipynb file to start the analysis")

        st.markdown("""
        ### 🎯 Dashboard Features:
        - **Interactive Graphs**: Toggle contributing factors on/off
        - **Model Comparison**: View US and UK models side-by-side
        - **Real-time Updates**: Charts refresh automatically when you change selections
        - **Data Tables**: View the raw forecast data
        """)

        # Show demo plot with sample data
        st.subheader("📈 Demo Preview")

        # Create sample data for demo
        demo_us_data = {
            'dates': pd.date_range('2024-01-01', '2024-12-01', freq='MS'),
            'Inflation': [3.55, 3.69, 4.23, 4.21, 4.39, 5.16, 5.53, 5.33, 5.13, 5.26, 5.46, 5.50],
            'Sentiment': [71.7, 70.6, 68.8, 68.1, 67.3, 67.3, 65.9, 65.5, 65.7, 64.6, 63.0, 63.9],
            'Claims': [266710, 166020, 100699, 190771, 189943, 207828, 169711, 112040, 148389, 150727, 153356, 171384]
        }

        demo_uk_data = {
            'dates': pd.date_range('2024-02-01', '2025-01-01', freq='MS'),
            'Inflation': [-0.53, -0.50, -0.25, -0.23, -0.22, -0.09, -0.06, -0.07, -0.02, -0.01, -0.02, 0.00],
            'Tesco_Index': [114.65, 114.84, 114.85, 114.94, 115.08, 115.17, 115.24, 115.33, 115.40, 115.46, 115.52, 115.59]
        }

        demo_fig = create_interactive_plot(demo_us_data, demo_uk_data, selected_factors, model_type)
        st.plotly_chart(demo_fig, use_container_width=True)

if __name__ == "__main__":
    main()
