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

    # Step 2: Clean district name
    def clean_district_name(district_name):
        """Clean district names, ensuring consistent formatting."""
        replacements = {
            'Ã¢Â€Â”': ' ', 'Ã¢Â€Â‘': ' ', '—': ' ', '–': ' ', '-': ' ',
            '1000': 'Thousand', '&': 'and', '’': "'"
        }
        for old, new in replacements.items():
            district_name = district_name.replace(old, new)
        return re.sub(r"\s*\(.*\)$", "", district_name).strip()

    # Extract district name
    district_name = None
    try:
        district_name_tag = soup.find('div', class_='noads').find('h2')
        if district_name_tag:
            district_name = clean_district_name(district_name_tag.get_text(strip=True))
    except AttributeError:
        return []

    if not district_name:
        return []

    # Step 3: Text Processing in HTML
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
                # Clean and filter text
                text = f"{date} OLP {olp} NDP {ndp} PCPO {pcpo} GPO {gpo}"
                text = re.sub(r"(\d+%)", r"\1 ", text)
                text = re.sub(r"(\d{4}-\d{2}-\d{2})(?=\d{4}-\d{2}-\d{2})", r"\1 ", text)
                text = re.sub(r"(\d{4}-\d{2}-\d{2})(\S)", r"\1 \2", text)
                text = re.sub(r"(\d{4})(\d{4})", r"\2", text)
                dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)

                seen_dates = set()
                unique_dates = [date for date in dates if date not in seen_dates and not seen_dates.add(date)]
                text = re.sub(r"\d{4}-\d{2}-\d{2}", lambda match: unique_dates.pop(0) if unique_dates else "", text)

                olp_percentages = re.findall(r"OLP\s*(\d+%)", text) or ["0%"] * len(unique_dates)
                pcpo_percentages = re.findall(r"PCPO\s*(\d+%)", text) or ["0%"] * len(unique_dates)
                ndp_percentages = re.findall(r"NDP\s*(\d+%)", text) or ["0%"] * len(unique_dates)
                gpo_percentages = re.findall(r"GPO\s*(\d+%)", text) or ["0%"] * len(unique_dates)

                min_len = min(len(unique_dates), len(olp_percentages), len(pcpo_percentages), len(ndp_percentages), len(gpo_percentages))
                unique_dates = unique_dates[:min_len]
                olp_percentages = olp_percentages[:min_len]
                pcpo_percentages = pcpo_percentages[:min_len]
                ndp_percentages = ndp_percentages[:min_len]
                gpo_percentages = gpo_percentages[:min_len]

                for i in range(min_len):
                    data.append({
                        "District": district_name,
                        "Date": unique_dates[i],
                        "OLP": olp_percentages[i],
                        "NDP": ndp_percentages[i],
                        "PCPO": pcpo_percentages[i],
                        "GPO": gpo_percentages[i]
                    })

    return data

# List of all possible districts (example list, replace with actual district names)
all_districts = ["Brampton East", "Cambridge", "Oakville North Burlington", "Timiskaming Cochrane"]

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
        
        # Find missing districts
        extracted_districts = set(df['District'].unique())
        missing_districts = set(all_districts) - extracted_districts
        print(f"Missing districts: {missing_districts}")
    else:
        print("No data to save.")

# Example usage
urls_file = './_Provincial/ProvUrls.txt'
output_csv_file = './_Provincial/Prov_data.csv'

process_urls_and_extract_data
