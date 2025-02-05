from tqdm import tqdm  # Import the tqdm library for progress bar
import requests
from bs4 import BeautifulSoup
import sys
from os import path
import pandas as pd
sys.path.append(path.abspath(path.join(path.dirname(__file__), "..")))
import functions as f


# Step 1: Get the URL from ...txt
def read_urls_from_file(file_path):
    """Read the URLs from the file and return them as a list."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


# Step 1.2 Extract data from the given URL
def extract_district_data(url):
    """Extract district data from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        return []

    page_content = response.content.decode('utf-8', 'ignore')
    soup = BeautifulSoup(page_content, 'html.parser')

    # Step 2: Clean district name
    # Extract district name
    district_name = None
    try:
        district_name_tag = soup.find('div', class_='noads').find('h2')
        if district_name_tag:
            district_name = f.clean_district_name(district_name_tag.get_text(strip=True))
    except AttributeError:
        return []

    if not district_name:
        return []

    # Step 3: Text Processing in HTML
    data = f.extract_polling_data(soup, district_name)
    return data


# Step 7: Process and print data (for all URLs)
def process_urls_and_extract_data(urls_file, output_csv_file):
    urls = read_urls_from_file(urls_file)
    all_data = []

    # Process all URLs from the list
    for url in tqdm(urls, desc="Processing URLs", unit="URL", leave=True):
        data = extract_district_data(url)
        if data:
            all_data.extend(data)

    if all_data:
        df = pd.DataFrame(all_data)
        
        # Remove duplicate rows per district and date, keep only the first occurrence
        df = df.drop_duplicates(subset=['District', 'Date'], keep='first')
        
        df.to_csv(output_csv_file, index=False)
        print(f"Data saved to {output_csv_file}")
        
        # Find missing districts (backlog)
        # f.check_missing_districts(df, )

    else:
        print("No data to save.")


# Example usage
urls_file = './_Provincial/ProvUrls.txt'
output_csv_file = './_Provincial/Prov_data.csv'

process_urls_and_extract_data(urls_file, output_csv_file)
