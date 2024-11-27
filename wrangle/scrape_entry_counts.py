from datetime import datetime
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import time

# Constants
START_DATE = datetime(2024, 8, 27)
MAX_WEEK = 99  # Temporary limit for testing

def calculate_week(date):
    date_obj = datetime.strptime(date, "%m/%d/%y")
    delta = date_obj - START_DATE
    return delta.days // 7

def init_driver():
    # Setup Chrome options
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')  # Run in headless mode
    return webdriver.Chrome(options=chrome_options)

def signin(driver, email, password, signin_url):
    try:
        # Visit signin page
        driver.get(signin_url)
        
        # Wait for and find email input
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "page_signin_email"))
        )
        email_input.send_keys(email)
        
        # Find and fill password
        password_input = driver.find_element(By.ID, "page_signin_password")
        password_input.send_keys(password)
        
        # Find and click submit button that is within the auth-form class
        submit_button = driver.find_element(By.CSS_SELECTOR, "form.auth-form input[type='submit']")
        submit_button.click()
        
        # Wait for login to complete by looking for user menu
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "header-user-name"))
            )
            print("Successfully signed in")
        except Exception as e:
            print("Warning: Could not verify successful sign-in:", str(e))
            
        # Extra wait to ensure page loads
        time.sleep(2)
        
    except Exception as e:
        print(f"Error during sign-in: {str(e)}")
        raise

def count_nonzero_scores(driver, url):
    """Count entries with scores >= 1.0 until first score < 1.0 is found"""
    entry_count = 0
    current_url = url
    done = False
    
    while not done:
        # Visit the page
        driver.get(current_url)
        
        # Wait for table to load
        try:
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table"))
            )
            
            # Find all score cells (using the number class in the last column)
            rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
            
            for row in rows:
                # Get score from the last cell
                score_cell = row.find_elements(By.CLASS_NAME, "number")[-1]
                score_text = score_cell.text.strip()
                
                try:
                    score = float(score_text)
                    if score >= 1.0:
                        entry_count += 1
                    else:
                        done = True
                        break
                except ValueError:
                    print(f"Warning: Could not parse score: {score_text}")
                    continue
            
            # If we haven't found a zero score and there are more pages
            if not done:
                # Look for next page link
                next_page = driver.find_elements(By.CSS_SELECTOR, "a.next_page")
                if next_page and next_page[0].is_enabled():
                    current_url = next_page[0].get_attribute("href")
                else:
                    done = True
            
        except Exception as e:
            print(f"Error processing page: {str(e)}")
            break
    
    return entry_count

def process_weekly_entries():
    # Load environment variables
    load_dotenv(os.path.join('..', '.env'))
    blackout_url = os.getenv('BLACKOUT_URL')
    signin_url = os.getenv('SIGNIN_URL')
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    
    if not all([blackout_url, signin_url, email, password]):
        raise ValueError("Missing required environment variables")
        
    # Define file path with year
    current_year = datetime.now().year
    file_path = f"../data/{current_year}_entry_counts.csv"
    
    # Read existing CSV if it exists
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print(f"Found existing {current_year}_entry_counts.csv")
    else:
        df = pd.DataFrame(columns=['year', 'week', 'entries'])
        print(f"Creating new {current_year}_entry_counts.csv")
        
    # current_year already defined above in file_path
    
    # Initialize the driver
    driver = init_driver()
    
    try:
        # Sign in first
        signin(driver, email, password, signin_url)
        
        # Visit the blackout URL
        driver.get(blackout_url)
        
        # Wait for the competition week pager to load
        week_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "competition-week-pager"))
        )
        
        # Process weeks 1 through MAX_WEEK
        for week_number in range(1, MAX_WEEK + 1):
            # Skip if we already have data for this week
            if not df[(df['year'] == current_year) & (df['week'] == week_number)].empty:
                print(f"Week {week_number} already processed, skipping...")
                continue

            # Re-fetch the week container and elements each time
            driver.get(blackout_url)  # Return to main page
            time.sleep(1)  # Give page time to load
            
            week_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "competition-week-pager"))
            )
            
            # Find element for this specific week
            week_elements = week_container.find_elements(By.CSS_SELECTOR, f"a.week, div.week")
            week_element = None
            week_url = None
            
            # Find matching week element
            for element in week_elements:
                try:
                    if int(element.text.strip()) == week_number:
                        week_element = element
                        if element.get_attribute("href"):
                            week_url = element.get_attribute("href")
                        else:
                            week_url = blackout_url if "--current" in element.get_attribute("class") else None
                        break
                except Exception as e:
                    continue
                
            if week_url:
                print(f"Processing Week {week_number}...")
                entry_count = count_nonzero_scores(driver, week_url)
                print(f"Found {entry_count} non-zero entries for Week {week_number}")
                
                # Add new row to DataFrame
                new_row = pd.DataFrame({
                    'year': [current_year],
                    'week': [week_number],
                    'entries': [entry_count]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Save after each week
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                df.to_csv(file_path, index=False)
                print(f"Updated {file_path} with Week {week_number} data")
                
        return df
        
    finally:
        driver.quit()

if __name__ == "__main__":
    process_weekly_entries()