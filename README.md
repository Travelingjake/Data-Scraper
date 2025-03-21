# Data-Scraper

## Overview
Data-Scraper is a set of scripts designed to automate the extraction of voting projection data for federal and provincial electoral districts. The scripts fetch data from a specified website, process it, and save it into CSV files for analysis and tracking.

## Components
### 1. Federal URL Lister
The **Federal URL Lister** script:
- Enters the federal index page that lists all federal electoral districts.
- Identifies and lists URLs associated with each district number.
- **Note**: An exception exists for the three territories, which are currently being populated incorrectly and listed multiple times. This is an issue pending resolution.

### 2. Federal Data Extractor
The **Federal Data Extractor** script:
- Reads URLs listed by the Federal URL Lister from `FedUrls.txt`.
- Visits each district’s page and extracts available data from the popular vote projection graph.
- Saves the processed data for each district into a CSV file.

### 3. Provincial URL Lister
The **Provincial URL Lister** script:
- Enters the provincial index page that lists all provincial electoral districts.
- Identifies and lists URLs associated with each district number.
  
### 4. Provincial Data Extractor
The **Provincial Data Extractor** script:
- Reads URLs listed by the Provincial URL Lister from `ProvUrls.txt`.
- Visits each district’s page and extracts available data from the popular vote projection graph.
- Saves the processed data for each district into a CSV file.

## Usage
1. Run the **Federal URL Lister** or **Provincial URL Lister** script to populate `FedUrls.txt` or `ProvUrls.txt` with URLs for each district.
2. Run the **Federal Data Extractor** or **Provincial Data Extractor** script to extract data from each district’s page and save it to a CSV file.

### Note
Ensure all dependencies are installed, and update file paths as needed to match your setup.

## Requirements
- Python 3.8 or later
- Required Python packages (listed in `requirements.txt`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/data-scraper.git
