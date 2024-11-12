import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from tqdm import tqdm  # Import the tqdm library for progress bar

# Function to read URLs from the 'urls.txt' file
def read_urls_from_file(file_path):
    """Read the URLs from the file and return them as a list."""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to clean district name by fixing encoding issues and dashes
def clean_district_name(district_name):
    """Clean district names, ensuring consistent formatting with spaces and hyphens."""
    # Replace misinterpreted characters and dashes
    district_name = district_name.replace('Ã¢Â€Â”', ' ')  # Misinterpreted em dash
    district_name = district_name.replace('Ã¢Â€Â‘', ' ')  # Misinterpreted en dash
    district_name = district_name.replace('—', ' ')  # Replace em dash with space
    district_name = district_name.replace('–', ' ')  # Replace en dash with space
    district_name = district_name.replace('-', ' ')  # Replace hyphen with space

    # Replace '1000' with 'Thousand' and '&' with 'and'
    district_name = district_name.replace('1000', 'Thousand')
    district_name = district_name.replace('&', 'and')

    # Replace special apostrophes
    district_name = district_name.replace('’', "'")  # Normalize curly apostrophes

    # Remove text in parentheses (if any)
    district_name = re.sub(r"\s*\(.*\)$", "", district_name)  # Remove text in parentheses

    return district_name.strip()

# Function to extract district data from a given URL
def extract_district_data(url):
    """Extract district data from the given URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Failed to connect to {url}. Status code: {response.status_code}")
        return "Failed to connect"

    page_content = response.content.decode('utf-8', 'ignore')
    soup = BeautifulSoup(page_content, 'html.parser')

    # Extract and clean the district name
    district_name_element = soup.find('div', class_='noads')
    if not district_name_element:
        return "No district name found"

    district_name = district_name_element.find('h2').get_text(strip=True)
    district_name = clean_district_name(district_name)

    # Log the district name
    print(f"Processing District: {district_name}")

    data = []
    for item in soup.find_all('div', class_='hideifmobile'):
        text = item.get_text(strip=True)

        # Patterns for extracting data
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        pcpo_pattern = r"PCPO\s*(\d+%)"
        olp_pattern = r"OLP\s*(\d+%)"
        ndp_pattern = r"NDP\s*(\d+%)"
        gpo_pattern = r"GPO\s*(\d+%)"

        dates = re.findall(date_pattern, text)
        pcpo_percentages = re.findall(pcpo_pattern, text) or ["0%"] * len(dates)
        olp_percentages = re.findall(olp_pattern, text) or ["0%"] * len(dates)
        ndp_percentages = re.findall(ndp_pattern, text) or ["0%"] * len(dates)
        gpo_percentages = re.findall(gpo_pattern, text) or ["0%"] * len(dates)

        # Ensure all lists have the same length by trimming to the minimum length
        min_len = min(len(dates), len(pcpo_percentages), len(olp_percentages), len(ndp_percentages), len(gpo_percentages))

        # Adjust all lists to length min_len
        dates = dates[:min_len]
        pcpo_percentages = pcpo_percentages[:min_len]
        olp_percentages = olp_percentages[:min_len]
        ndp_percentages = ndp_percentages[:min_len]
        gpo_percentages = gpo_percentages[:min_len]

        # Append data to the list
        for i in range(min_len):
            data.append({
                "District": district_name,
                "Date": dates[i] if i < len(dates) else "N/A",  # Handle missing dates as "N/A"
                "PCPO": pcpo_percentages[i],
                "OLP": olp_percentages[i],
                "NDP": ndp_percentages[i],
                "GPO": gpo_percentages[i]
            })

    return data if data else "No polling data found"


# Function to write data to CSV, replacing previous data
def write_to_csv(file_path, data):
    """Write district data to CSV, replacing the previous data.""" 
    df = pd.DataFrame(data)

    # Fill missing columns with '0%' if any are missing in the DataFrame
    for column in ["PCPO", "OLP", "NDP", "GPO"]:
        if column not in df.columns:
            df[column] = '0%'

    # Save the data to the CSV file, overwriting previous content
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

# Main processing function
def process_urls_and_extract_data(urls_file, output_csv_file):
    """Process all URLs, extract district data, and save to CSV."""
    urls = read_urls_from_file(urls_file)
    all_district_data = []
    failed_urls = []

    # Use tqdm for progress bar
    for url in tqdm(urls, desc="Processing URLs", unit="URL"):
        result = extract_district_data(url)
        if isinstance(result, list):
            all_district_data.extend(result)
        else:
            failed_urls.append((url, result))

    # Write the collected data to the CSV file, replacing previous data
    if all_district_data:
        write_to_csv(output_csv_file, all_district_data)
    else:
        print("No valid data extracted.")

    # Output the reasons for failed URLs
    if failed_urls:
        print("\nThe following URLs were not processed:")
        for url, reason in failed_urls:
            print(f"{url} - Reason: {reason}")

# Example usage
urls_file = 'C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/ProvUrls.txt'  # Path to your URLs list
output_csv_file = 'C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/Provincial_district_data.csv'  # Path to the output CSV file

# Process the URLs and write the extracted data to CSV
process_urls_and_extract_data(urls_file, output_csv_file)