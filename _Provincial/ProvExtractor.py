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
    except AttributeError:
        return []

    if not district_name:
        return []

    # Step 3.1: Text Processing in HTML
    data = []
    for textbox in soup.find_all('g', class_='textbox'):
        texts = textbox.find_all('text')
        if texts:
            date = None
            olp = ndp = pcpo = gpo = "0%"
            for text in texts:
                text_content = text.get_text(strip=True)
                if re.match(r"\d{4}-\d{2}-\d{2}", text_content):
                    date = text_content
                elif "OLP" in text_content:
                    percentage = re.search(r"(\d+%)", text_content)
                    if percentage:
                        olp = percentage.group(1)
                elif "NDP" in text_content:
                    percentage = re.search(r"(\d+%)", text_content)
                    if percentage:
                        ndp = percentage.group(1)
                elif "PCPO" in text_content:
                    percentage = re.search(r"(\d+%)", text_content)
                    if percentage:
                        pcpo = percentage.group(1)
                elif "GPO" in text_content:
                    percentage = re.search(r"(\d+%)", text_content)
                    if percentage:
                        gpo = percentage.group(1)
            
            if date:
                data.append({
                    "District": district_name,
                    "Date": date,
                    "OLP": olp,
                    "NDP": ndp,
                    "PCPO": pcpo,
                    "GPO": gpo
                })

    return data

# Step 7: Process and print data (for all URLs)
def process_urls_and_extract_data(urls_file, output_csv_file):
    urls = read_urls_from_file(urls_file)
    all_data = []

    # Process all URLs from the list
    for url in tqdm(urls, desc="Processing URLs", unit="URL"):
        data = extract_district_data(url)
        if data:
            all_data.extend(data)

    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_csv_file, index=False)
        print(f"Data saved to {output_csv_file}")
    else:
        print("No data to save.")

# Example usage
urls_file = '_Provincial/ProvUrls.txt'
output_csv_file = '_Provincial/Prov_data.csv'

process_urls_and_extract_data(urls_file, output_csv_file)
