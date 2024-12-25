import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
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
st.title("Fantasy Index Blackout -- 2004 Usage Stats")

# Load data
@st.cache_data
def get_data():
    weekly_df = load_data()
    
    # Create aggregated dataframe
    agg_df = weekly_df.groupby(['Name', 'Position']).agg({
        'Week': 'nunique',  # Count unique weeks
        'Team': lambda x: x.iloc[-1],  # Get latest team
        'Score': 'sum',  # Sum of scores
        'Count': 'sum',  # Sum of counts
        'Entries': 'sum'  # Sum of entries
    }).reset_index()
    
    # Calculate average score per week
    agg_df['Score'] = agg_df['Score'] / agg_df['Week']
    
    # Calculate overall Start_Pct
    agg_df['Start_Pct'] = (agg_df['Count'] / agg_df['Entries']) * 100
    
    # Set Week to "All"
    agg_df['Week'] = 'All'
    
    # Round numeric columns
    agg_df['Score'] = agg_df['Score'].round(1)
    agg_df['Start_Pct'] = agg_df['Start_Pct'].round(1)
    
    # Combine weekly and aggregated data
    combined_df = pd.concat([weekly_df, agg_df[weekly_df.columns]], ignore_index=True)
    
    return combined_df

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
        positions = ["All"] + [p for p in available_positions if p != "All"]
        selected_position = st.selectbox("Select Position", positions)
    
    with col2:
        # Week filter with "All" first, then numeric weeks
        numeric_weeks = sorted(w for w in df["Week"].unique() if w != "All")
        weeks = ["All"] + numeric_weeks
        selected_week = st.selectbox("Select Week", weeks, index=0)  # index=0 selects "All"
    
    # Filter data based on selections
    filtered_df = df.copy()
    if selected_position != "All":
        filtered_df = filtered_df[filtered_df["Position"] == selected_position]
    if selected_week != "All":
        filtered_df = filtered_df[filtered_df["Week"] == selected_week]
    else:
        filtered_df = filtered_df[filtered_df["Week"] == "All"]
    
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
                    x=pos_df["Score"],
                    y=pos_df["Start_Pct"],
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
                z = np.polyfit(pos_df["Score"], pos_df["Start_Pct"], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(pos_df["Score"].min(), pos_df["Score"].max(), 100)
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
                        showlegend=False,
                        hoverinfo='skip'  # Disable hover tooltips for trendline
                    )
                )
    
    # Update layout
    title_suffix = " (Average among weeks available in contest)" if selected_week == "All" else f" (Week {selected_week})"
    fig.update_layout(
        height=600,
        title=f"Player Start Percentage vs Score{title_suffix}",
        xaxis_title="Player Score",
        yaxis_title="Start Percentage (%)",
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
        # Create a copy of the dataframe for display
        display_df = filtered_df[display_columns.keys()].copy()
        st.dataframe(
            display_df
            .rename(columns=display_columns)
            .sort_values('Start Pct', ascending=False),
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.info("Please make sure the SHEET_URL environment variable is properly set.")