import requests
from bs4 import BeautifulSoup
import re
import csv
import time

# Headers for the HTTP request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

proxies = {
    'http': 'http://207.244.217.165:6712',
    'https': 'http://207.244.217.165:6712'
}

# URL of the GPU benchmark page
url = "https://www.videocardbenchmark.net/high_end_gpus.html"

# Send an HTTP GET request to fetch the page content
response = requests.get(url, proxies=proxies, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Wait for a few seconds in case there are delays in loading the page
    time.sleep(3)
    
    # Find the <ul> element with class 'charlist'
    ul_element = soup.find('ul', class_='chartlist')
    
    if ul_element:
        # Get all <li> elements inside the <ul>
        list_items = ul_element.find_all('li')

        
        pattern = re.compile(r"([A-Za-z0-9\s\.\-\+@]+)\s*\((\d+)%\)\s*([\d,]+)\s*([NA\$]*[\d,.]*)")

        data = ""
        # Loop through the list items and extract the text
        for item in list_items:
            data+=(item.get_text()+"\n")


        with open('Final Year Project/gpu_benchmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write header
            csvwriter.writerow(['GPU Name', 'Performance (%)', 'Benchmark Score', 'Price'])

            # Find all matches of the pattern in the data
            for match in pattern.findall(data):
                gpu_name = match[0].strip()
                performance = match[1]
                benchmark_score = match[2].replace(",", "")  # Remove commas from numbers
                price = match[3] if match[3] else 'NA'

                # Write the row to the CSV file
                csvwriter.writerow([gpu_name, performance, benchmark_score, price])

        print("Data has been successfully written to gpu_benchmarks.csv")

# import re
# import requests
# from bs4 import BeautifulSoup
# import csv

# # Headers for the HTTP request
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }

# proxies = {
#     'http': 'http://207.244.217.165:6712',
#     'https': 'http://207.244.217.165:6712'
# }

# # URL of the GPU benchmark page
# url = "https://www.videocardbenchmark.net/high_end_gpus.html"

# # Send an HTTP GET request to fetch the page content
# response = requests.get(url, proxies=proxies, headers=headers)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the HTML content with BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find the table or list with GPU data
#     ul_element = soup.find('ul', class_='chartlist')

#     if ul_element:
#         # Open CSV file for writing
#         with open('gpu_benchmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
#             csvwriter = csv.writer(csvfile)

#             # Write the header row
#             csvwriter.writerow(['GPU Name', 'Score (%)', 'Benchmark', 'Price (USD)'])

#             # Loop through each list item
#             for item in ul_element.find_all('li'):
#                 # Extract the text content of the list item
#                 text = item.get_text(strip=True)

#                 # Split the data into components
#                 parts = re.split(r'\s*(?=\()|\s*(?<=\))|(?<=\))(?=\d)|(?<=\d)\s*(?=\d)', text)

#                 if len(parts) >= 4:
#                     gpu_name = parts[0].strip()  # GPU name
#                     score = parts[1].strip() if '(' in parts[1] else 'N/A'  # Extract score (e.g., 86%)
#                     benchmark = parts[2].strip().replace(',', '')  # Remove commas from benchmark
#                     price = parts[3].strip() if parts[3].startswith('$') else 'N/A'  # Price, if available
#                 else:
#                     gpu_name = text.strip()
#                     score = 'N/A'
#                     benchmark = 'N/A'
#                     price = 'N/A'

#                 # Write the extracted and cleaned data to the CSV file
#                 csvwriter.writerow([gpu_name, score, benchmark, price])

#         print("Data has been successfully written to gpu_benchmarks.csv")
#     else:
#         print("ul_element not found on the page!")
# else:
#     print(f"Failed to fetch the webpage. Status code: {response.status_code}")

