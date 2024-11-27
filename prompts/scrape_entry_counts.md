# Fantasy Index Blackout Entry Counter

## Project Overview
Create a web scraper to track participation in Fantasy Index's Blackout competition by counting active entries each week. An "active entry" is defined as any entry scoring 1.0 points or higher.

## Data Structure
- Input: Web pages with nested navigation:
  1. Start page contains links to each week's standings
  2. Each week's standings spread across multiple pages (100 entries per page)
  3. Each page contains a table with columns: Rank, Team Name, Location, Score
- Output: YYYY_entry_counts.csv with columns:
  - year: Current 4-digit year
  - week: Week number (1-17)
  - entries: Count of active entries that week

## Navigation Logic
1. Start Page
   - Login required - use Selenium to:
     - Visit signin page
     - Enter email/password from .env
     - Submit form and verify login success
   - Find week links in "competition-week-pager" container
   - Process each available week not already in CSV

2. Week Pages
   - For each week's standings URL:
     - Visit first page
     - Process entries table
     - Follow "next_page" links until either:
       - Finding first score < 1.0, or
       - No more pages exist

3. Entry Tables
   - Find table rows in tbody
   - For each row:
     - Extract score from last column (has class="number")
     - Convert to float and compare to 1.0
     - Stop counting when first sub-1.0 score found

## Implementation Requirements
1. Environment Setup
   ```
   .env file containing:
   BLACKOUT_URL=https://fantasyindex.com/members/competitions/2024/blackout/standings/...
   SIGNIN_URL=https://fantasyindex.com/signin
   EMAIL=your_email
   PASSWORD=your_password
   ```

2. Dependencies
   ```
   selenium
   pandas
   python-dotenv
   ```

3. Key Functions Needed
   ```python
   def signin(driver, email, password, signin_url):
       # Handle login process
   
   def count_nonzero_scores(driver, url):
       # Process single week's pages
       # Return count of scores >= 1.0
   
   def process_weekly_entries():
       # Main function that:
       # 1. Reads existing CSV if present
       # 2. Gets list of week URLs
       # 3. Processes each unrecorded week
       # 4. Saves results after each week
   ```

4. Error Handling
   - Handle stale elements by re-fetching after page navigation
   - Verify login success before proceeding
   - Handle pagination edge cases
   - Save progress after each week

5. File Management
   - Store CSVs in ../data/ directory
   - Name format: YYYY_entry_counts.csv
   - Create directories if needed
   - Check for existing data before scraping

## Example Usage
```python
if __name__ == "__main__":
    process_weekly_entries()
```

## Expected Output
```csv
# 2024_entry_counts.csv
year,week,entries
2024,1,837
2024,2,792
...
```

## Implementation Tips
1. Return to main standings page between weeks to avoid stale elements
2. Add short delays after page loads for stability
3. Use WebDriverWait for elements rather than fixed delays
4. Save progress frequently in case of interruption
5. Consider adding logging for debugging