#This version is able to enter the current set of data in a proper format


import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime

# Path to your ChromeDriver
chrome_driver_path = "C:/Users/trave/Desktop/Verts OV Greens/Data Scraper/chromedriver-win64/chromedriver.exe"  # Adjust path if necessary

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: Runs Chrome in headless mode (without opening a browser window)
chrome_options.add_argument("--ignore-certificate-errors")

# Create a Service object for the ChromeDriver
service = Service(chrome_driver_path)

# Set up the WebDriver
driver = webdriver.Chrome(service=service, options=chrome_options)

# Open the website
url = "https://338canada.com/35081e.htm"
driver.get(url)

# Wait for the div with the class 'hideifmobile' to be present
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='hideifmobile']"))
    )
    print("Found the div with class 'hideifmobile'")
except Exception as e:
    print(f"Error: {e}")

# Find the div and extract content
try:
    div = driver.find_element(By.XPATH, "//div[@class='hideifmobile']")
    content = div.text.strip()  # Extract text from the div
    print("Content extracted")
except Exception as e:
    print(f"Content not found: {e}")

# Process the content to extract relevant data
if content:
    # Use regex to extract the dates and percentages for each party
    data = []
    date_pattern = r"\d{4}-\d{2}-\d{2}"
    lpc_pattern = r"LPC\s*(\d+%)"
    cpc_pattern = r"CPC\s*(\d+%)"
    ndp_pattern = r"NDP\s*(\d+%)"
    gpc_pattern = r"GPC\s*(\d+%)"

    # Find all the dates
    dates = re.findall(date_pattern, content)
    
    # Find the corresponding percentages for each party
    lpc_percentages = re.findall(lpc_pattern, content)
    cpc_percentages = re.findall(cpc_pattern, content)
    ndp_percentages = re.findall(ndp_pattern, content)
    gpc_percentages = re.findall(gpc_pattern, content)

    # Make sure all lists have the same length (if any are shorter, align them)
    min_len = min(len(dates), len(lpc_percentages), len(cpc_percentages), len(ndp_percentages), len(gpc_percentages))
    dates = dates[:min_len]
    lpc_percentages = lpc_percentages[:min_len]
    cpc_percentages = cpc_percentages[:min_len]
    ndp_percentages = ndp_percentages[:min_len]
    gpc_percentages = gpc_percentages[:min_len]

    # Combine the extracted data into a list of dictionaries
    for i in range(min_len):
        data.append({
            "Date": dates[i],
            "LPC Percentage": lpc_percentages[i],
            "CPC Percentage": cpc_percentages[i],
            "NDP Percentage": ndp_percentages[i],
            "GPC Percentage": gpc_percentages[i]
        })

    # Convert the data into a pandas DataFrame and save it to CSV
    if data:
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"scrapped_data_{today}.csv"
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
    else:
        print("No valid data extracted.")
else:
    print("No content found in the div")

# Close the driver
driver.quit()
