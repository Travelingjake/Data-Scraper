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
            print(f"Found district name: {district_name}")  # Debugging output
    except AttributeError:
        print(f"District name not found for URL: {url}")
        return []

    if not district_name:
        print(f"District name not found for URL: {url}")
        return []

    # Step 3.1: Text Processing in HTML
    data = []
    for item in soup.find_all('div', class_='hideifmobile'):
        text = item.get_text(strip=True)

        # Processing each item to extract useful data
        comma_index = text.find(',')
        if comma_index != -1:
            text = text[comma_index+1:].strip()

        odds_index = re.search(r"(x?odds)", text, re.IGNORECASE)
        if odds_index:
            text = text[:odds_index.start()].strip()

#Step 3.1 Adds a space to the right of %
        text = re.sub(r"(\d+%)", r"\1 ", text)

#Step 3.2 Dates Clearing (yyyy-mm// ddx... to dd x...) and (yyyy-mm-dd [adds this space])
        text = re.sub(r"(\d{4}-\d{2}-\d{2})(?=\d{4}-\d{2}-\d{2})", r"\1 ", text)
        text = re.sub(r"(\d{4}-\d{2}-\d{2})(\S)", r"\1 \2", text)

#Step 3.3 Clears any 8 number string into the last 4 numbers (starting date)
        text = re.sub(r"(\d{4})(\d{4})", r"\2", text)

        #print(f"Nearly Cleaned: {text}")

# Step 3.4 Removes Date duplicates
        dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)

        seen_dates = set()
        unique_dates = []
        for date in dates:
         if date not in seen_dates:
            unique_dates.append(date)
            seen_dates.add(date)

        #date_iter = iter(unique_dates)
        text = re.sub(r"\d{4}-\d{2}-\d{2}", lambda match: unique_dates.pop(0) if unique_dates else "", text)

        #print(f"Final Cleaned Text: {text}")

#Step 3.5 Dates (YYYY-MM-DD format)

        dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)

        # Extracting dates and party percentages
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

        # Step 6: Add data to dictionary
        for i in range(min_len):
            data.append({
                "District": district_name,
                "Date": dates[i],
                "LPC": olp_percentages[i],
                "NDP": ndp_percentages[i],
                "CPC": pcpo_percentages[i],
                "GPC": gpo_percentages[i]
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
            all_data.extend(data)

    df = pd.DataFrame(all_data)
    df.to_csv(output_csv_file, index=False)
    print(f"Data saved to {output_csv_file}")

# Example usage
urls_file = 'C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/_Provincial/ProvUrls.txt'  
output_csv_file = 'C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/_Provincial/Provincial_district_data.csv'

process_urls_and_extract_data(urls_file, output_csv_file)
