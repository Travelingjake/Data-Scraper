from tqdm import tqdm  # Import the tqdm library for progress bar
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

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

    first_url = urls[0]
    print(f"🚀 Processing {first_url}...")
    data = extract_district_data(first_url)
    if data:
        print(f"✅ Extracted {len(data)} rows. Adding to all_data.")
        all_data.extend(data)
    else:
        print(f"⚠️ No data extracted from {first_url}. Skipping CSV update.")

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

