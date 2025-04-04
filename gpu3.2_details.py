import requests
from bs4 import BeautifulSoup
import time
import re
import csv

# Headers for the HTTP request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# URL of the Page
url = "https://www.videocardbenchmark.net/high_end_gpus.html"

# Proxies (if required)
proxies = {
    'http': 'http://207.244.217.165:6712',
    'https': 'http://207.244.217.165:6712'
}

# Send HTTP GET request to fetch the page content
response = requests.get(url, proxies=proxies, headers=headers)

# Function to extract specific fields from the description
def extract_field(description, field_name, regex_pattern):
    match = re.search(regex_pattern, description)
    return match.group(1) if match else "N/A"

# Function to truncate GPU name
def truncate_gpu_name(full_name):
    match = re.search(r'^(.*\(\d+%\))', full_name)
    return match.group(1) if match else full_name

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the <ul> element with class 'chartlist'
    ul_element = soup.find('ul', class_='chartlist')

    if ul_element:
        # Open CSV file for writing
        with open('Final Year Project/gpu3.2_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write header row
            csvwriter.writerow(['GPU Name', 'Benchmark', 'Max Memory Size', 'Max TDP', 'Videocard Category'])

            # Get all <li> elements in <ul>
            list_items = ul_element.find_all('li')

            for item in list_items:
                # Find anchor tag inside the <li> element
                a_tag = item.find('a')

                if a_tag and a_tag['href']:
                    # Get the GPU name from the <a> tag
                    gpu_name_full = a_tag.text.strip()
                    gpu_name = truncate_gpu_name(gpu_name_full)  # Truncate the GPU name
                    # Get the link to the next page
                    link = a_tag['href']

                    # If the link is relative, prepend the base URL
                    if not link.startswith('http'):
                        link = "https://www.videocardbenchmark.net/" + link

                    next_page_response = requests.get(link, proxies=proxies, headers=headers)

                    if next_page_response.status_code == 200:
                        next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')

                        # Find the description div
                        desc_div = next_page_soup.find('div', class_='desc')

                        if desc_div:
                            # Extract text from the description div
                            description = desc_div.text.strip()

                            # Extract required fields using regex
                            benchmark_match = re.search(r'\((\d+)%\)\s*([\d,]+)', item.get_text(strip=True))
                            benchmark = benchmark_match.group(2).replace(',', '') if benchmark_match else "N/A"
                            max_memory_size = extract_field(description, 'Max Memory Size', r'Max Memory Size:\s*([\d,]+ MB)')
                            max_tdp = extract_field(description, 'Max TDP', r'Max TDP:\s*([\d,]+ W)')
                            videocard_category = extract_field(description, 'Videocard Category', r'Videocard Category:\s*([^\n]+)')

                            # Write data to CSV
                            csvwriter.writerow([gpu_name, benchmark, max_memory_size, max_tdp, videocard_category])

                            print(f"Extracted: {gpu_name}, {benchmark}, {max_memory_size}, {max_tdp}, {videocard_category}")
                        else:
                            print(f"No description found for {gpu_name}")
                    else:
                        print(f"Failed to load page for {gpu_name}. Status code: {next_page_response.status_code}")

                    # To avoid overwhelming the server, pause briefly
                    time.sleep(1)

    else:
        print("The UL element with class 'chartlist' was not found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
