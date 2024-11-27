import pandas as pd
import requests
from io import StringIO
import streamlit as st

def load_data(sheet_url=None):
    """
    Load and transform player selection data from Google Sheet.
    If no URL provided, loads from Streamlit secrets.
    
    Returns:
    pandas.DataFrame: Transformed data with columns [Week, Count, Score, Name, Position, Team, Start_Pct]
    """
    if sheet_url is None:
        if 'SHEET_URL' not in st.secrets:
            raise ValueError("SHEET_URL not found in Streamlit secrets")
        sheet_url = st.secrets['SHEET_URL']

    # Convert sharing URL to export URL
    sheet_id = sheet_url.split('/')[5]
    gid = sheet_url.split('gid=')[1].split('#')[0]
    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    # Download and read CSV data
    response = requests.get(export_url)
    response.raise_for_status()
    df = pd.read_csv(StringIO(response.text), skiprows=2)
    
    # Detect weeks and initialize data collection
    num_weeks = len(df.columns) // 7
    transformed_data = []
    
    # Process each row and week
    for _, row in df.iterrows():
        for week in range(1, num_weeks + 1):
            start_idx = (week-1) * 7
            
            try:
                name = row.iloc[start_idx + 4]
                count = row.iloc[start_idx + 1]
                total = row.iloc[start_idx + 2]  # This is the percentage column
                
                if pd.notna(name) and pd.notna(count) and str(count).strip() and str(name).strip():
                    transformed_data.append({
                        'Week': week,
                        'Count': count,
                        'Start_Pct': float(str(total).strip('%')) if pd.notna(total) else 0,
                        'Score': row.iloc[start_idx + 3],
                        'Name': name.strip(),
                        'Position': row.iloc[start_idx + 5].strip(),
                        'Team': row.iloc[start_idx + 6].strip()
                    })
            except (IndexError, ValueError):
                continue
    
    if not transformed_data:
        raise ValueError("No valid data was found in the sheet")
    
    # Create DataFrame and convert types
    result_df = pd.DataFrame(transformed_data)
    
    # Convert numeric columns
    numeric_columns = ['Week', 'Count', 'Score', 'Start_Pct']
    for col in numeric_columns:
        result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
    
    result_df['Week'] = result_df['Week'].fillna(0).astype(int)
    result_df['Count'] = result_df['Count'].fillna(0).astype(int)
    
    # Filter invalid rows
    result_df = result_df[
        (result_df['Count'] > 0) & 
        (result_df['Week'] > 0) & 
        (result_df['Name'].notna()) & 
        (result_df['Name'] != '')
    ]
    
    return result_df.sort_values(['Week', 'Count'], ascending=[True, False])