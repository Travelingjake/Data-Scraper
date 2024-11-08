import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

# Define the URL to scrape
url = "https://338canada.com/35081e.htm"

# Send a GET request to the website
response = requests.get(url)
response.encoding = 'utf-8'  # Explicitly set the encoding to utf-8

if response.status_code == 200:
    print("Successfully connected to the website!")
else:
    print(f"Failed to connect. Status code: {response.status_code}")

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Extract the district name from the specific <h2> tag within the <div class="noads">
district_name = soup.find('div', class_='noads').find('h2').get_text(strip=True)

# Replace hyphens ('—') with spaces
district_name = district_name.replace('—', ' ')

# Extract the polling data from <div class="hideifmobile">
data = []
for item in soup.find_all('div', class_='hideifmobile'):
    text = item.get_text(strip=True)
    
    # Use regex to extract polling information
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    lpc_pattern = r"LPC\s*(\d+%)"
    cpc_pattern = r"CPC\s*(\d+%)"
    ndp_pattern = r"NDP\s*(\d+%)"
    gpc_pattern = r"GPC\s*(\d+%)"

    dates = re.findall(date_pattern, text)
    lpc_percentages = re.findall(lpc_pattern, text)
    cpc_percentages = re.findall(cpc_pattern, text)
    ndp_percentages = re.findall(ndp_pattern, text)
    gpc_percentages = re.findall(gpc_pattern, text)

    # Ensure all lists have the same length
    min_len = min(len(dates), len(lpc_percentages), len(cpc_percentages), len(ndp_percentages), len(gpc_percentages))
    dates = dates[:min_len]
    lpc_percentages = lpc_percentages[:min_len]
    cpc_percentages = cpc_percentages[:min_len]
    ndp_percentages = ndp_percentages[:min_len]
    gpc_percentages = gpc_percentages[:min_len]

    # Add the district name to each row and populate data
    for i in range(min_len):
        data.append({
            "District": district_name,
            "Date": dates[i],
            "LPC": lpc_percentages[i],
            "CPC": cpc_percentages[i],
            "NDP": ndp_percentages[i],
            "GPC": gpc_percentages[i]
        })

# Convert the data into a DataFrame and save to CSV
if data:
    today = datetime.now().strftime("%Y-%m-%d")
    filename = f"scraped_data_{today}.csv"
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
else:
    print("No valid data extracted.")
