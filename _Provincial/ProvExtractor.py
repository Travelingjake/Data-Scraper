from tqdm import tqdm  # Import the tqdm library for progress bar
import requests
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
import pandas as pd
import re

# Step 1: Get the URL from ...txt
def read_urls_from_file(file_path):
    """Read the URLs from the file and return them as a list."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Step 1.2 Extract data from the given URL using Selenium to handle hover
def extract_district_data(url):
    """Extract district data from the given URL, handling hover events using Selenium."""
    # Setup Selenium WebDriver (make sure to have ChromeDriver or another driver installed)
    driver = webdriver.Chrome(executable_path='/path/to/chromedriver')  # Adjust path if needed
    driver.get(url)
    
    # Wait for the page to load fully (adjust timing as needed)
    time.sleep(3)

    # Find the element that triggers the hover (you'll need to inspect the page and update this)
    hover_element = driver.find_element(By.CSS_SELECTOR, ".hover-target-class")

    # Simulate the hover action
    actions = ActionChains(driver)
    actions.move_to_element(hover_element).perform()
    
    # Wait a moment for the hover effect to show the necessary data
    time.sleep(1)  # Adjust as needed to give the page time to show the data

    # Now that the hover is done, extract the page source
    page_content = driver.page_source
    driver.quit()

    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(page_content, 'html.parser')

    # Step 2.1: Clean district name
    def clean_district_name(district_name):
        """Clean district names, ensuring consistent formatting."""
        district_name = district_name.replace('Ã¢Â€Â”', ' ')  # Misinterpreted em dash
        district_name = district_name.replace('Ã¢Â€Â‘', ' ')  # Misinterpreted en dash
        district_name = district_name.replace('—', ' ')  # Replace em dash with space
        district_name = district_name.replace('–', ' ')  # Replace en dash with space
        district_name = district_name.replace('-', ' ')  # Replace hyphen with space
        district_name = district_name.replace('1000', 'Thousand')  # Replace '1000' with 'Thousand'
        district_name = district_name.replace('&', 'and')  # Replace '&' with 'and'
        district_name = district_name.replace('’', "'")  # Normalize curly apostrophes
        district_name = re.sub(r"\s*\(.*\)$", "", district_name)  # Remove text in parentheses
        return district_name.strip()

    # Extract district name (adjusting to the structure of the page)
    district_name = None
    try:
        district_name_tag = soup.find('div', class_='noads').find('h2')
        if district_name_tag:
            district_name = clean_district_name(district_name_tag.get_text(strip=True))
            print(f"✅Found district name: {district_name}")  # Debugging output
    except AttributeError:
        print(f"❌District name not found for URL: {url}")
        return []

    if not district_name:
        print(f"⚠️District name not found for URL: {url}")
        return []

    # Extract data from the page
    data = []
    textbox = soup.find('g', class_='textbox')
    if not textbox:
        print(f"⚠️ No polling data found for {district_name}. Skipping.")
        return []
    
    texts = textbox.find_all('text')
    if len(texts) < 5:
        print(f"⚠️ Insufficient polling data found for {district_name}. Skipping.")
        return []
    
    date = texts[0].get_text(strip=True)
    pcpo = re.search(r"PCPO (\d+%)", texts[1].get_text(strip=True))
    olp = re.search(r"OLP (\d+%)", texts[2].get_text(strip=True))
    ndp = re.search(r"NDP (\d+%)", texts[3].get_text(strip=True))
    gpo = re.search(r"GPO (\d+%)", texts[4].get_text(strip=True))
    
    data.append({
        "District": district_name,
        "Date": date,
        "PCPO": pcpo.group(1) if pcpo else "0%",
        "OLP": olp.group(1) if olp else "0%",
        "NDP": ndp.group(1) if ndp else "0%",
        "GPO": gpo.group(1) if gpo else "0%"
    })

    if not data:
        print(f"⚠️ No formatted data found for {district_name}.")
    return data

# Step 7: Process and print data (for one URL)
def process_urls_and_extract_data(urls_file, output_csv_file):
    urls = read_urls_from_file(urls_file)
    all_data = []

    # Process all URLs
    for url in tqdm(urls, desc="Processing URLs", unit="URL"):
        print(f"🚀 Processing {url}...")
        data = extract_district_data(url)
        if data:
            print(f"✅ Extracted {len(data)} rows. Adding to all_data.")
            all_data.extend(data)
        else:
            print(f"⚠️ No data extracted from {url}. Skipping CSV update.")

    # Create DataFrame from all extracted data
    df = pd.DataFrame(all_data)
    if df.empty:
        print("⚠️ DataFrame is EMPTY. No data to save!")
    else:
        print(f"📊 DataFrame has {df.shape[0]} rows. Saving to CSV.")
        df.to_csv(output_csv_file, index=False)
        print(f"✅ Data saved to {output_csv_file}")

    # Adding tqdm for the progress bar while processing URLs
    #for url in tqdm(urls, desc="Processing URLs", unit="URL"):
    #    print(f"Processing {url}...")
    #    data = extract_district_data(url)
    #    if data:
    #        all_data.extend(data)

    #df = pd.DataFrame(all_data)
    #df.to_csv(output_csv_file, index=False)
    #print(f"Data saved to {output_csv_file}")

# Example usage
urls_file = './_Provincial/ProvUrls.txt'  # Use relative path for input URL file
output_csv_file = './_Provincial/Provincial_district_data.csv'  # Use relative path for output CSV file

process_urls_and_extract_data(urls_file, output_csv_file)
