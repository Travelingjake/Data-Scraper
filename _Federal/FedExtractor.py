from tqdm import tqdm  # Import the tqdm library for progress bar
import requests
from bs4 import BeautifulSoup
from os import path
import sys
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
        print(f"Failed to connect to {url}. Status code: {response.status_code}")
        return []

    page_content = response.content.decode('utf-8', 'ignore')
    soup = BeautifulSoup(page_content, 'html.parser')

    # Step 2.1: Clean district name
    # Extract district name (adjusting to the structure of the page)
    district_name = None
    try:
        district_name_tag = soup.find('div', class_='noads').find('h2')
        if district_name_tag:
            district_name = f.clean_district_name(district_name_tag.get_text(strip=True))
            print(f"Found district name: {district_name}")  # Debugging output
    except AttributeError:
        print(f"District name not found for URL: {url}")
        return []

    if not district_name:
        print(f"District name not found for URL: {url}")
        return []

    # Step 3.1: Text Processing in HTML
    data = f.extract_polling_data(soup, district_name)

    return data


# Step 7: Process and print data (for one URL)
def process_urls_and_extract_data(urls_file, output_csv_file, looker=None):
    urls = read_urls_from_file(urls_file)
    all_data = []

    # Adding tqdm for the progress bar while processing URLs
    for url in tqdm(urls, desc="Processing URLs", unit="URL"):
        print(f"Processing {url}...")
        data = extract_district_data(url)
        if data:
            all_data.extend(data)

    df = pd.DataFrame(all_data)
    if not df.empty:
        df.to_csv(output_csv_file, index=False)
        print(f"Data saved to {output_csv_file}")
        if looker:
            df_looker = f.depivot_data(df)
            df_looker.to_csv(looker, index=False)
            df_looker.to_csv(path.join(
                '..', 'survey-pipeline-prod', 'resources',
                f'{looker[str.rfind(looker, '/')+1:]}'.replace('_looker', '')))
            print(f"Data saved to looker file {looker_csv_file}")
    else:
        print("Dataframe empty, something wrong with code/requests")


# Example usage
urls_file = './_Federal/FedUrls.txt'  # Use relative path for input URL file
output_csv_file = './_Federal/Federal_district_data.csv'  # Use relative path for output CSV file
looker_csv_file = './_Federal/Federal_district_data_looker.csv'  # Use relative path for output CSV file
process_urls_and_extract_data(urls_file, output_csv_file, looker=looker_csv_file)
