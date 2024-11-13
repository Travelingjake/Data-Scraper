import requests
from bs4 import BeautifulSoup

# Define the URL to scrape
base_url = "https://338canada.com"
district_url = f"{base_url}/federal.htm" 

# Define output
fed_file_path = "C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/_Federal/FedUrls.txt"

# Function to read existing URLs from the file
def read_existing_urls(file_path):
    try:
        with open(file_path, 'r') as file:
            existing_urls = set(file.read().splitlines())  # Using a set to avoid duplicates
        return existing_urls
    except FileNotFoundError:
        # If the file doesn't exist yet, return an empty set
        return set()

# Function to write new URLs to the file
def write_urls_to_file(file_path, new_urls):
    with open(file_path, 'w') as file:
        for url in new_urls:
            file.write(url + '\n')

# Send a GET request to the website
response = requests.get(district_url)
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
     # Filter for URLs containing district number patterns; add base_url if needed
    if ("/100" in href or "/110" in href or "/120" in href or "/130" in href or
        "/240" in href or "/350" in href or "/351" in href or "/460" in href or
        "/470" in href or "/480" in href or "/590" in href): 
        full_url = href if href.startswith("http") else base_url + href  # Ensure URL is absolute
        district_urls.append(full_url)

# Read the existing URLs
existing_urls = read_existing_urls(fed_file_path)

# Create a set of new URLs from the extracted ones (to remove duplicates)
new_urls = set(district_urls)

# Compare existing and new URLs and find the differences
urls_to_add = new_urls - existing_urls
urls_to_remove = existing_urls - new_urls

# If there are changes, update the file
if urls_to_add or urls_to_remove:
    updated_urls = existing_urls.union(urls_to_add)  # Add new URLs
    write_urls_to_file(fed_file_path, updated_urls)
    print(f"URLs updated. Added {len(urls_to_add)} new URLs and removed {len(urls_to_remove)} old URLs.")
else:
    print("No changes in URLs. The list is up-to-date.")
