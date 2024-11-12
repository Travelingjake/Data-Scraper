#This version is able to enter the site and corectly extract all data points but all in one cell

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# Define the URL to scrape
url = "https://338canada.com/ontario/1083e.htm"

# Send a GET request to the website
response = requests.get(url)
if response.status_code == 200:
    print("Successfully connected to the website!")
else:
    print(f"Failed to connect. Status code: {response.status_code}")

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Example: Find all elements with a specific tag (<div>) or class (class_='hideifmobile)
# Replace 'tag' and 'class_name' with actual values
data = []
for item in soup.find_all('div', class_='hideifmobile'):
    # Extract information (modify this part according to the website structure)
    text = item.get_text(strip=True)
    data.append(text)

# Save data to CSV
today = datetime.now().strftime("%Y-%m-%d")
filename = f"scrapped_data_{today}.csv"
df = pd.DataFrame(data, columns=['Extracted Data'])
df.to_csv(filename, index=False)
print("Data saved to {filename}")
