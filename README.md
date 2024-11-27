# Fantasy Index Blackout Stats Dashboard

A Streamlit dashboard for visualizing player usage and performance data from the [Fantasy Index Blackout](https://fantasyindex.com/members/competitions/2024/blackout) game. The dashboard displays player start percentages versus scores, with interactive filtering by position and week.

## Features

- Interactive scatter plot showing the relationship between player start percentages and scores
- Position-specific trendlines
- Filtering by position and week
- Detailed player tooltips with comprehensive stats
- Sortable data table with raw statistics
- Position-based color coding for easy visual analysis
- Auto-defaults to the latest available week

## Prerequisites

- Python 3.8+
- A Google Sheet URL containing Fantasy Index Blackout data
- Access to the Fantasy Index Blackout competition data

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ffi-blackout-stats.git
cd ffi-blackout-stats
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Configure Streamlit secrets by creating `.streamlit/secrets.toml`:
```toml
SHEET_URL = "your_google_sheet_url_here"
```

4. Create an `assets` directory and add your FFI logo:
```bash
mkdir assets
# Add FFI_logo.svg to the assets directory
```

## Usage

Run the Streamlit app:
```bash
streamlit run FFI_blackout_stats.py
```

The dashboard will be available at `http://localhost:8501` by default.

## Project Structure

```
ffi-blackout-stats/
├── FFI_blackout_stats.py  # Main Streamlit application
├── utils.py               # Data loading and processing utilities
├── assets/               
│   └── FFI_logo.svg      # Fantasy Index logo
├── .streamlit/
│   └── secrets.toml      # Streamlit secrets (not in repo)
└── requirements.txt      # Python dependencies
```

## Required Packages

- streamlit
- plotly
- pandas
- numpy
- requests

## Secrets Management

This app uses Streamlit's secrets management feature. Create a `.streamlit/secrets.toml` file with:

```toml
SHEET_URL = "your_google_sheet_url_here"
```

For deployment:
1. Local development: Place the secrets.toml file in the `.streamlit` directory
2. Streamlit Cloud: Add secrets through the Streamlit Cloud dashboard
3. Other platforms: Follow the platform's secure secrets management guidelines

Note: Never commit the secrets.toml file to version control.

## Data Structure

The Google Sheet should contain weekly player data with the following columns:
1. Checksum (unused)
2. Count (number of selections)
3. Percent (start percentage)
4. Score
5. Name (player/team name)
6. Position (QB, RB, WR, TE, PK, ST)
7. Team (NFL team abbreviation)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Acknowledgments

- Fantasy Index for providing the competition data
- Streamlit for the web application framework
- Plotly for interactive visualizations