import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

#Step 1.1 Website Request
url = "https://338canada.com/35081e.htm"

response = requests.get(url)
if response.status_code == 200:
    print("Successfully connected to the website!")
else:
    print(f"Failed to connect. Status code: {response.status_code}")

#Step 1.2 Extract Data from the HTML
soup = BeautifulSoup(response.text, 'html.parser')
data = {}
for item in soup.find_all('div', class_='hideifmobile'):

#Step 2.1 Text Processing
    text = item.get_text(strip=True)

#Step 2.2 Clears everything before the ',' and then everything after 'odds'
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

    date_iter = iter(unique_dates)
    text = re.sub(r"\d{4}-\d{2}-\d{2}", lambda match: unique_dates.pop(0) if unique_dates else "", text)

    print(f"Final Cleaned Text: {text}")

#Step 3.5 Dates (YYYY-MM-DD format)

    dates = re.findall(r"\d{4}-\d{2}-\d{2}", text)

# Step 4: Extract each party's percentage, or set to '0%' if not found
    lpc_percentages = re.findall(r"LPC\s*(\d+%)", text) or ["0%"] * len(dates)
    cpc_percentages = re.findall(r"CPC\s*(\d+%)", text) or ["0%"] * len(dates)
    ndp_percentages = re.findall(r"NDP\s*(\d+%)", text) or ["0%"] * len(dates)
    gpc_percentages = re.findall(r"GPC\s*(\d+%)", text) or ["0%"] * len(dates)
    
# Ensure all lists (dates, party percentages) have the same length by trimming to the shortest list
    min_len = min(len(dates), len(lpc_percentages), len(cpc_percentages), len(ndp_percentages), len(gpc_percentages))
    
# Trim all lists to the minimum length to avoid mismatched data
    dates = dates[:min_len]
    lpc_percentages = lpc_percentages[:min_len]
    cpc_percentages = cpc_percentages[:min_len]
    ndp_percentages = ndp_percentages[:min_len]
    gpc_percentages = gpc_percentages[:min_len]
    
    
# Step 5: Add data for each date into the dictionary, ensuring only one entry per date
    for i in range(min_len):
        date = dates[i]
        
# Print the final date for each entry
        print(f"Final Date: {date}")
        
        data[date] = {
            "Date": date,
            "LPC": lpc_percentages[i],
            "NDP": ndp_percentages[i],
            "CPC": cpc_percentages[i],
            "GPC": gpc_percentages[i]
        }

# Convert data dictionary to a list of dictionaries
data_list = list(data.values())

# Now, process the dates and percentages to clean and isolate the most recent data
processed_data = []

# Loop through the data and apply transformations to the dates and percentages
for entry in data_list:
# Reformat the date if needed
    date = entry["Date"]
    
 # Extract the polling percentages and clean the formatting
    lpc = entry["LPC"]
    ndp = entry["NDP"]
    cpc = entry["CPC"]
    gpc = entry["GPC"]
    
# Check if dates need to be processed and ensure only the most recent date is kept
    match = re.match(r"(\d{4}-\d{2}-\d{2})(\d{4}-\d{2}-\d{2})", date)
    if match:
        date_1 = match.group(1)
        date_2 = match.group(2)
        
# Keep only the second date as it's the most recent
        date = date_2
    
# Reformat the extracted data for the current entry
    processed_data.append({
        "Date": date,
        "LPC": lpc,
        "NDP": ndp,
        "CPC": cpc,
        "GPC": gpc
    })

# Debugging: Print the cleaned data as a string before parsing into DataFrame
print("Processed Data (Before Parsing to DataFrame):")
for entry in processed_data:
    print(f"{entry['Date']} - LPC: {entry['LPC']}, NDP: {entry['NDP']}, CPC: {entry['CPC']}, GPC: {entry['GPC']}")

# Convert the processed data into a DataFrame
df = pd.DataFrame(processed_data)

# Convert the DataFrame to a CSV
today = datetime.now().strftime("%Y-%m-%d")
filename = f"scraped_data_{today}.csv"
df.to_csv(filename, index=False)

# Output confirmation of saved data
print(f"Data saved to {filename}")
