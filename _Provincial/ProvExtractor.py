from tqdm import tqdm  # Import the tqdm library for progress bar
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

# Step 1: Get the URL from ...txt
def read_urls_from_file(file_path):
    """Read the URLs from the file and return them as a list."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return [line.strip() for line in file.readlines()]

# Step 2: Extract data from the given URL
def extract_district_data(url):
    """Extract district data from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Failed to connect to {url}. Status code: {response.status_code}")
        print(response.text)  # For debugging
        return []

    print(f"Successfully connected to {url}")

    page_content = response.content.decode('utf-8', 'ignore')
    soup = BeautifulSoup(page_content, 'html.parser')

    # Step 3: Clean district name
    def clean_district_name(district_name):
        """Clean district names for consistency."""
        replacements = {
            'Ã¢Â€Â”': ' ', 'Ã¢Â€Â‘': ' ', '—': ' ', '–': ' ', '-': ' ',
            '1000': 'Thousand', '&': 'and', '’': "'"
        }
        for old, new in replacements.items():
            district_name = district_name.replace(old, new)
        return re.sub(r"\s*\(.*\)$", "", district_name).strip()

    district_name = None
    try:
        district_container = soup.find('div', class_='noads')
        if district_container:
            district_name_tag = district_container.find('h2')
            if district_name_tag:
                district_name = clean_district_name(district_name_tag.get_text(strip=True))
            else:
                print("District name not found in 'h2' tag.")
        else:
            print("District container not found.")
    except AttributeError:
        print(f"Error extracting district name from URL: {url}")
        return []

    if not district_name:
        print(f"District name not found for URL: {url}")
        return []

    # Step 4: Text Processing in HTML
    data = []
    for item in soup.find_all('div', class_='hideifmobile'):
        text = item.get_text(strip=True)

        # Debugging: print text found in the div
        print(f"Extracted text: {text[:100]}...")  # Show first 100 characters for review

        # Processing each item to extract useful data
        comma_index = text.find(',')
        if comma_index != -1:
            text = text[comma_index + 1:].strip()

        odds_index = re.search(r"(x?odds)", text, re.IGNORECASE)
        if odds_index:
            text = text[:odds_index.start()].strip()

        # Add additional text cleaning steps here...

        # Extracting party percentages
        olp_percentages = re.findall(r"OLP\s*(\d+%)", text) or ["0%"] * len(dates)
        pcpo_percentages = re.findall(r"PCPO\s*(\d+%)", text) or ["0%"] * len(dates)
        ndp_percentages = re.findall(r"NDP\s*(\d+%)", text) or ["0%"] * len(dates)
        gpo_percentages = re.findall(r"GPO\s*(\d+%)", text) or ["0%"] * len(dates)

        # Ensure same length for all lists
        min_len = min(len(dates), len(olp_percentages), len(pcpo_percentages), len(ndp_percentages), len(gpo_percentages))
        dates = dates[:min_len]
        olp_percentages = olp_percentages[:min_len]
        pcpo_percentages = pcpo_percentages[:min_len]
        ndp_percentages = ndp_percentages[:min_len]
        gpo_percentages = gpo_percentages[:min_len]

        # Add data to list
        for i in range(min_len):
            data.append({
                "District": district_name,
                "Date": dates[i],
                "OLP": olp_percentages[i],
                "NDP": ndp_percentages[i],
                "PCPO": pcpo_percentages[i],
                "GPO": gpo_percentages[i]
            })

    return data


# Step 7: Process and print data (for one URL)
def process_urls_and_extract_data(urls_file, output_csv_file):
    urls = read_urls_from_file(urls_file)
    all_data = []

    # Adding tqdm for the progress bar while processing URLs
    for url in tqdm(urls, desc="Processing URLs", unit="URL"):
        print(f"Processing {url}...")
        data = extract_district_data(url)
        if data:
            print(f"Extracted data from {url}: {data}")  # For debugging
            all_data.extend(data)

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_csv_file, index=False)
        print(f"Data saved to {output_csv_file}")
    else:
        print("No data extracted. Check the URLs and the scraping logic.")

# Example usage
urls_file = './_Provincial/ProvUrls.txt'  # Use relative path for input URL file
output_csv_file = './_Provincial/Provincial_district_data.csv'  # Use relative path for output CSV file
process_urls_and_extract_data(urls_file, output_csv_file)
