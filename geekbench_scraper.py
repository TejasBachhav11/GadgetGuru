import requests
from bs4 import BeautifulSoup
import time
import re
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# URL of the page to scrape
url = "https://browser.geekbench.com/processor-benchmarks"
BASE_URL = "https://browser.geekbench.com"
MAIN_URL = f"{BASE_URL}/processor-benchmarks"

proxies = {
    'http': 'http://207.244.217.165:6712',
    'https': 'http://207.244.217.165:6712'
}

# Send an HTTP GET request to fetch the page content
response = requests.get(url, proxies=proxies, headers=headers)

# Function to scrape main benchmark table
def scrape_main_table(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='benchmark-chart-table')
    processors = []

    for row in table.find('tbody').find_all('tr'):
        cols = row.find_all('td')
        name_cell = cols[0]
        score = cols[1].text.strip()

        # Get processor name and link to its detail page
        name = name_cell.text.strip()
        link = BASE_URL + name_cell.find('a')['href']

        processors.append({
            'name': name,
            'score': score,
            'link': link
        })
    
    return processors

# Function to scrape additional details from each processor page
def scrape_processor_details(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # CPU table data
    cpu_table = soup.find('table', class_='cpu')
    cpu_details = {}
    if cpu_table:
        for row in cpu_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                cpu_details[cells[0].text.strip()] = cells[1].text.strip()

    # System table data
    system_table = soup.find('table', class_='system-table')
    system_details = {}
    if system_table:
        for row in system_table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                system_details[cells[0].text.strip()] = cells[1].text.strip()

    return cpu_details, system_details

# Main function to scrape all processor data
def main():
    processors = scrape_main_table(MAIN_URL)
    all_data = []

    for processor in processors:
        print(f"Scraping details for {processor['name']}")
        cpu_details, system_details = scrape_processor_details(processor['link'])
        
        # Combine all information into a single dictionary
        data = {
            'Name': processor['name'],
            'Score': processor['score'],
            **cpu_details,
            **system_details
        }
        all_data.append(data)
        
        # Be polite and avoid overloading the server
        time.sleep(1)

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(all_data)
    df.to_csv('geekbench-processor_benchmarks.csv', index=False)
    print("Data saved to processor_benchmarks.csv")

if __name__ == "__main__":
    main()