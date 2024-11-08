import requests
from bs4 import BeautifulSoup

# Define the URL to scrape
url = "https://338canada.com/districts.htm"

# Send a GET request to the website
response = requests.get(url)
response.encoding = 'utf-8'  # Explicitly set the encoding to utf-8

if response.status_code == 200:
    print("Successfully connected to the website!")
else:
    print(f"Failed to connect. Status code: {response.status_code}")

# Parse the HTML content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all the <a> tags that link to the district pages
links = soup.find_all('a', href=True)

# Extract URLs that likely correspond to district pages
district_urls = []
for link in links:
    href = link['href']
    # Check if the URL contains any of the specified patterns
    if ("/100" in href or "/110" in href or "/120" in href or "/130" in href or
        "/240" in href or "/350" in href or "/351" in href or "/460" in href or
        "/470" in href or "/480" in href or "/590" in href): 
# For some reason within the pages code it seems to populate 30...
#  iterations of the three teritorial district so they are being omitted
        district_urls.append(href)

# Print the list of URLs found
if district_urls:
    print(f"Found {len(district_urls)} district URLs:")
    for url in district_urls:
        print(url)
else:
    print("No district URLs found.")
