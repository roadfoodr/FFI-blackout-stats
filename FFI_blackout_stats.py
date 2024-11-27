import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils import load_data
import os

# Page config
st.set_page_config(
    page_title="Fantasy Index Blackout",
    page_icon="🏈",
    layout="wide"
)

# Add logo with hyperlink
logo_path = "./assets/FFI_logo.svg"
if os.path.exists(logo_path):
    with open(logo_path, "rb") as f:
        logo_content = f.read().decode()
    
    st.markdown(
        f'<a href="https://fantasyindex.com/members/competitions/2024/blackout" target="_blank">'
        f'<div style="width:150px">{logo_content}</div>'
        f'</a>', 
        unsafe_allow_html=True
    )
    
# Title
st.title("Fantasy Index Blackout -- Usage Stats")

# Load data
@st.cache_data
def get_data():
    return load_data()

try:
    df = get_data()
    
    # Define position order and colors
    POSITION_ORDER = ["All", "QB", "RB", "WR", "TE", "PK", "ST"]
    POSITION_COLORS = {
        "QB": "#1f77b4",
        "RB": "#ff7f0e",
        "WR": "#2ca02c",
        "TE": "#d62728",
        "PK": "#9467bd",
        "ST": "#8c564b"
    }
    
    # Add filters in a row
    col1, col2 = st.columns(2)
    
    with col1:
        # Position filter with custom order
        available_positions = sorted(df["Position"].unique(), key=lambda x: POSITION_ORDER.index(x))
        positions = ["All"] + available_positions
        selected_position = st.selectbox("Select Position", positions)
    
    with col2:
        # Week filter with latest week as default
        weeks = ["All"] + sorted(df["Week"].unique().tolist())
        default_week = max(df["Week"].unique()) if len(df["Week"].unique()) > 0 else "All"
        selected_week = st.selectbox("Select Week", weeks, index=weeks.index(default_week))
    
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_position != "All":
        filtered_df = filtered_df[filtered_df["Position"] == selected_position]
    if selected_week != "All":
        filtered_df = filtered_df[filtered_df["Week"] == selected_week]
    
    # Create scatter plot with trendlines
    fig = go.Figure()
    
    # Get positions to plot in correct order
    if selected_position == "All":
        positions_to_plot = [pos for pos in POSITION_ORDER[1:] if pos in df["Position"].unique()]
    else:
        positions_to_plot = [selected_position]
    
    # Plot each position
    for pos in positions_to_plot:
        pos_df = filtered_df[filtered_df["Position"] == pos]
        
        # Add scatter points
        if len(pos_df) > 0:
            fig.add_trace(
                go.Scatter(
                    x=pos_df["Start_Pct"],
                    y=pos_df["Score"],
                    mode="markers",
                    name=pos,
                    marker=dict(color=POSITION_COLORS[pos]),
                    text=pos_df.apply(
                        lambda x: f"Name: {x['Name']}<br>Position: {x['Position']}<br>Team: {x['Team']}<br>Week: {x['Week']}<br>Score: {x['Score']:.1f}<br>Start Pct: {x['Start_Pct']:.1f}%", 
                        axis=1
                    ),
                    hoverinfo="text"
                )
            )
            
            # Add trendline
            if len(pos_df) > 1:
                z = np.polyfit(pos_df["Start_Pct"], pos_df["Score"], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(pos_df["Start_Pct"].min(), pos_df["Start_Pct"].max(), 100)
                fig.add_trace(
                    go.Scatter(
                        x=x_trend,
                        y=p(x_trend),
                        mode="lines",
                        name=pos,
                        line=dict(
                            dash="dash",
                            color=POSITION_COLORS[pos]
                        ),
                        showlegend=False
                    )
                )
    
    # Update layout
    fig.update_layout(
        height=600,
        title="Player Start Percentage vs Score",
        xaxis_title="Start Percentage (%)",
        yaxis_title="Player Score",
        legend_title="Position",
        hovermode='closest'
    )
    
    # Display plot
    st.plotly_chart(fig, use_container_width=True)
    
    # Display data table
    if st.checkbox("Show Raw Data", value=True):
        display_columns = {
            'Week': 'Week',
            'Name': 'Name',
            'Position': 'Position',
            'Team': 'Team',
            'Score': 'Score',
            'Start_Pct': 'Start Pct'
        }
        st.dataframe(
            filtered_df[display_columns.keys()]
            .rename(columns=display_columns)
            .sort_values('Start Pct', ascending=False),
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure the SHEET_URL environment variable is properly set.")