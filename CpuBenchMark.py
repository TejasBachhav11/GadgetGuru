import requests
from bs4 import BeautifulSoup
import time
import re
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


# URL of the page to scrape
url = "https://www.cpubenchmark.net/laptop.html"

proxies = {
    'http': 'http://207.244.217.165:6712',
    'https': 'http://207.244.217.165:6712'
}
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

        
        pattern = re.compile(r"([A-Za-z0-9\s\.\-\+@]+)\((\d+)%\)([\d,]+)([NA\$]*[\d,.]*)")
        data = ""
        # Loop through the list items and extract the text
        for item in list_items:
            data+=(item.get_text()+"\n")


        with open('Final Year Project/cpu_benchmarks.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)

            # Write header
            csvwriter.writerow(['Processor Name', 'Performance (%)', 'Benchmark Score', 'Price'])

            # Find all matches of the pattern in the data
            for match in pattern.findall(data):
                processor_name = match[0].strip()
                performance = match[1]
                benchmark_score = match[2].replace(",", "")  # Remove commas from numbers
                price = match[3] if match[3] else 'NA'

                # Write the row to the CSV file
                csvwriter.writerow([processor_name, performance, benchmark_score, price])

        print("Data has been successfully written to cpu_benchmarks.csv")



    else:
        print("The UL element with class 'charlist' was not found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
