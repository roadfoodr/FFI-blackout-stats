import pandas as pd
import requests
from io import StringIO
import streamlit as st

def load_data(sheet_url=None):
    """
    Load and transform player selection data from Google Sheet.
    If no URL provided, loads from Streamlit secrets.
    
    Returns:
    pandas.DataFrame: Transformed data with columns [Week, Count, Entries, Score, Name, Position, Team, Start_Pct]
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
    
    # Try to load the entries data
    try:
        if 'ENTRIES_URL' in st.secrets:
            entries_url = st.secrets['ENTRIES_URL']
            entries_sheet_id = entries_url.split('/')[5]
            entries_gid = entries_url.split('gid=')[1].split('#')[0]
            entries_export_url = f"https://docs.google.com/spreadsheets/d/{entries_sheet_id}/export?format=csv&gid={entries_gid}"
            
            entries_response = requests.get(entries_export_url)
            entries_response.raise_for_status()
            start_entries = pd.read_csv(StringIO(entries_response.text))
            have_entries = True
        else:
            have_entries = False
    except Exception:
        have_entries = False
    
    # Detect weeks and initialize data collection
    num_weeks = len(df.columns) // 7
    transformed_data = []
    
    # Process each row and week
    for row_idx, row in df.iterrows():
        for week in range(1, num_weeks + 1):
            start_idx = (week-1) * 7
            
            try:
                name = row.iloc[start_idx + 4]
                count = row.iloc[start_idx + 1]
                total = row.iloc[start_idx + 2]  # Original percentage
                
                if pd.notna(name) and pd.notna(count) and str(count).strip() and str(name).strip():
                    entry = {
                        'Week': week,
                        'Count': count,
                        'Score': row.iloc[start_idx + 3],
                        'Name': name.strip(),
                        'Position': row.iloc[start_idx + 5].strip(),
                        'Team': row.iloc[start_idx + 6].strip(),
                        'Start_Pct': float(total.strip('%')) if pd.notna(total) and isinstance(total, str) else 0
                    }
                    transformed_data.append(entry)
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
    
    # Add Entries column based on available data
    if have_entries:
        # Merge Entries data
        result_df = result_df.merge(
            start_entries[['Week', 'Entries']], 
            on='Week', 
            how='left'
        )
    else:
        # Add Entries as NA
        result_df['Entries'] = pd.NA
    
    # Estimate any missing Entries values using Count/Percent
    mask = result_df['Entries'].isna()
    result_df.loc[mask, 'Entries'] = (result_df.loc[mask, 'Count'] / (result_df.loc[mask, 'Start_Pct'] / 100)).round()
    
    # Calculate Start_Pct using actual Entries
    result_df['Start_Pct'] = (result_df['Count'] / result_df['Entries']) * 100
    
    # Reorder columns to put Entries after Count
    cols = result_df.columns.tolist()
    count_idx = cols.index('Count')
    cols.remove('Entries')
    cols.insert(count_idx + 1, 'Entries')
    result_df = result_df[cols]
    
    # Filter invalid rows
    result_df = result_df[
        (result_df['Count'] > 0) & 
        (result_df['Week'] > 0) & 
        (result_df['Name'].notna()) & 
        (result_df['Name'] != '')
    ]
    
    return result_df.sort_values(['Week', 'Start_Pct'], ascending=[True, False])