import os
import sys

# Define paths to lister and extractor scripts
provincial_path = r"C:\Users\trave\Desktop\Verts OV Greens\Data Scraper\_Provincial"
federal_path = r"C:\Users\trave\Desktop\Verts OV Greens\Data Scraper\_Federal"

# Prompt for user input
print("Select data extraction option:")
print("1: Provincial")
print("2: Federal")
choice = input("Enter choice (1 or 2): ")

if choice == '1':
    # Provincial setup
    os.chdir(provincial_path)
    print("Running Provincial URL Lister...")
    os.system("python ProvUrlLister.py")
    
    # Load updated URLs from ProvUrls.txt
    with open("ProvUrls.txt", 'r') as file:
        urls = file.read().splitlines()
    
    # Run the Provincial Extractor for each URL
    for url in urls:
        os.environ['CURRENT_URL'] = url  # Pass URL as an environment variable
        print(f"Running Provincial Extractor for {url}...")
        os.system("python ProvExtractor.py")

elif choice == '2':
    # Federal setup
    os.chdir(federal_path)
    print("Running Federal URL Lister...")
    os.system("python FedUrlLister.py")
    
    # Load updated URLs from FedUrls.txt
    with open("FedUrls.txt", 'r') as file:
        urls = file.read().splitlines()
    
    # Run the Federal Extractor for each URL
    for url in urls:
        os.environ['CURRENT_URL'] = url  # Pass URL as an environment variable
        print(f"Running Federal Extractor for {url}...")
        os.system("python FedExtractor.py")

else:
    print("Invalid choice. Exiting.")
    sys.exit(1)

print("Data extraction completed.")
