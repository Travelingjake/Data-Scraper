import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
from tqdm import tqdm  # Import the tqdm library for progress bar

# Function to read URLs from the 'urls.txt' file
def read_urls_from_file(file_path):
    """Read the URLs from the file and return them as a list"""
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]

# Function to extract district data from a given URL
def extract_district_data(url):
    """Extract district data from the given URL"""
    # Send a GET request to the website
    response = requests.get(url)
    response.encoding = 'utf-8'  # Explicitly set the encoding to utf-8
    
    # Check for a successful connection
    if response.status_code != 200:
        print(f"Failed to connect to {url}. Status code: {response.status_code}")
        return []

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract the district name from the specific <h2> tag within the <div class="noads">
    district_name = soup.find('div', class_='noads').find('h2').get_text(strip=True)
    district_name = district_name.replace('—', ' ')  # Replace hyphens with spaces

    # Extract the polling data from <div class="hideifmobile">
    data = []
    for item in soup.find_all('div', class_='hideifmobile'):
        text = item.get_text(strip=True)
        
        # Use regex to extract polling information
        date_pattern = r"\d{4}-\d{2}-\d{2}"
        pcpo_pattern = r"PCPO\s*(\d+%)"
        olp_pattern = r"OLP\s*(\d+%)"
        ndp_pattern = r"NDP\s*(\d+%)"
        gpo_pattern = r"GPO\s*(\d+%)"

        dates = re.findall(date_pattern, text)
        pcpo_percentages = re.findall(pcpo_pattern, text)
        olp_percentages = re.findall(olp_pattern, text)
        ndp_percentages = re.findall(ndp_pattern, text)
        gpo_percentages = re.findall(gpo_pattern, text)

        # Ensure all lists have the same length
        min_len = min(len(dates), len(pcpo_percentages), len(olp_percentages), len(ndp_percentages), len(gpo_percentages))
        dates = dates[:min_len]
        pcpo_percentages = pcpo_percentages[:min_len]
        olp_percentages = olp_percentages[:min_len]
        ndp_percentages = ndp_percentages[:min_len]
        gpo_percentages = gpo_percentages[:min_len]

        # Add the district name to each row and populate data
        for i in range(min_len):
            data.append({
                "District": district_name,
                "Date": dates[i],
                "PCPO": pcpo_percentages[i],
                "OLP": olp_percentages[i],
                "NDP": ndp_percentages[i],
                "GPO": gpo_percentages[i]
            })
    return data

# Function to write data to CSV, replacing previous data
def write_to_csv(file_path, data):
    """Write district data to CSV, replacing the previous data"""
    # Convert the data into a DataFrame
    df = pd.DataFrame(data)
    
    # Save the data to the CSV file, overwriting previous content
    df.to_csv(file_path, index=False)
    print(f"Data saved to {file_path}")

# Main processing function
def process_urls_and_extract_data(urls_file, output_csv_file):
    """Process all URLs, extract district data, and save to CSV"""
    # Read URLs from the file
    urls = read_urls_from_file(urls_file)
    
    # Prepare a list to collect the district data
    all_district_data = []
    
    # Use tqdm for progress bar
    for url in tqdm(urls, desc="Processing URLs", unit="URL"):
        district_data = extract_district_data(url)
        if district_data:
            all_district_data.extend(district_data)
    
    # Write the collected data to the CSV file, replacing previous data
    if all_district_data:
        write_to_csv(output_csv_file, all_district_data)
    else:
        print("No valid data extracted.")

# Example usage
urls_file = 'C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/ProvUrls.txt'  # Path to your URLs list
output_csv_file = 'C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/Provincial_district_data.csv'  # Path to the output CSV file

# Process the URLs and write the extracted data to CSV
process_urls_and_extract_data(urls_file, output_csv_file)
