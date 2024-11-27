# Fantasy Index Blackout - Usage Stats Dashboard

Create a Streamlit app to visualize and analyze fantasy football player usage data from the Fantasy Index Blackout game.

## Data Structure
- Data is sourced from a Google Sheet with weekly player selection data
- Each week contains 7 columns:
  1. Checksum (unused)
  2. Count (number of selections)
  3. Percent (start percentage)
  4. Score 
  5. Name (player/team name)
  6. Position (QB, RB, WR, TE, PK, ST)
  7. Team (NFL team abbreviation)

## Core Requirements

### Data Processing (utils.py)
- Load data from Google Sheet URL (from environment variable)
- Transform wide-format data into normalized DataFrame
- Calculate and store start percentage from the "Percent" column
- Clean and validate all data fields
- Return sorted DataFrame with essential columns

### Dashboard (app.py)
- Display Fantasy Index logo (from ./assets/FFI_logo.svg)
- Title: "Fantasy Index Blackout -- Usage Stats"
- Create interactive scatter plot of Start Percentage vs Score
  - Consistent color scheme by position
  - Position-specific trendlines
  - Hover tooltips with player details (Name, Position, Team, Week, Score, Start Pct)
  - Legend showing positions in standard order: QB, RB, WR, TE, PK, ST

### Filtering Controls
- Position dropdown (All, QB, RB, WR, TE, PK, ST)
- Week dropdown (All, plus all available weeks)

### Data Table
- Shown by default
- Columns in order: Week, Name, Position, Team, Score, Start Pct
- Sorted by Start Pct (descending)
- No index column displayed

## Technical Details
- Use Streamlit for the web interface
- Use Plotly for interactive visualizations
- Maintain consistent position colors across all views
- Handle all errors gracefully with user-friendly messages
- Cache data loading for performance
- Environment variable configuration for data source

## Required Packages
```bash
streamlit
plotly
pandas
numpy
requests
python-dotenv
```

## Usage
1. Set SHEET_URL in .env file
2. Run with: `streamlit run app.py`