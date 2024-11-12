import requests
import time
import logging

# Set up logging
logging.basicConfig(filename='scraper_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    
    try:
        print(f"Fetching data from: {url}")
        response = requests.get(url, headers=headers, timeout=10)  # Adjust timeout if needed
        response.raise_for_status()  # Will raise an exception for 4xx/5xx responses
        return response.text
    except requests.exceptions.Timeout:
        print(f"Timeout error when connecting to {url}")
        logging.error(f"Timeout error when connecting to {url}")
    except requests.exceptions.ConnectionError:
        print(f"Connection error when connecting to {url}")
        logging.error(f"Connection error when connecting to {url}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error {e.response.status_code} when connecting to {url}")
        logging.error(f"HTTP error {e.response.status_code} when connecting to {url}")
    except Exception as e:
        print(f"General error occurred when connecting to {url}: {str(e)}")
        logging.error(f"General error occurred when connecting to {url}: {str(e)}")
    return None

def process_urls(url_list):
    failed_urls = []
    
    for url in url_list:
        data = fetch_data(url)
        if data:
            # Process the data
            print(f"Successfully processed {url}")
        else:
            failed_urls.append(url)
            print(f"Failed to process {url}")
    
    if failed_urls:
        print("\nThe following URLs were not processed:")
        for url in failed_urls:
            print(f"- {url}")
            logging.error(f"Failed to process: {url}")
    
    return failed_urls

def extract_and_process_data(url):
    # Example function for extracting and processing data
    data = fetch_data(url)
    if data:
        # Process your data extraction here (e.g., using BeautifulSoup)
        print(f"Processing data for {url}")
        # Example: Parse the data (modify with actual extraction logic)
        # soup = BeautifulSoup(data, 'html.parser')
        # Extract needed information here
    else:
        print(f"Data not found for {url}")
        logging.error(f"No data found for {url}")

# Example URL list to process
url_list = [
    "https://338canada.com/ontario/1110e.htm",
    "https://338canada.com/ontario/1118e.htm",
    "https://338canada.com/ontario/1051e.htm"
    # Add more URLs as needed
]

# Call the function to process the URLs
failed_urls = process_urls(url_list)

# Further debugging information
if failed_urls:
    print("\nURLs that failed to process and their reasons:")
    for url in failed_urls:
        extract_and_process_data(url)
