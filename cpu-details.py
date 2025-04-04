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
    
    # Find the <ul> element with class 'chartlist'
    ul_element = soup.find('ul', class_='chartlist')
    
    if ul_element:
        # Get all <li> elements inside the <ul>
        list_items = ul_element.find_all('li')

        # Open CSV file for writing
        with open('Final Year Project/cpu_details.csv', 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write CSV header
            csvwriter.writerow(['Processor', 'Description'])

            # Loop through the list items and extract the text and links
            for item in list_items:
                # Find the anchor tag inside the <li> element
                a_tag = item.find('a')

                if a_tag and a_tag['href']:
                    processor_name = a_tag.text.strip()  # Get the processor name from the <a> tag
                    link = a_tag['href']  # Get the link to the next page

                    # If the link is relative, prepend the base URL
                    if not link.startswith('http'):
                        link = "https://www.cpubenchmark.net/" + link

                    # Fetch the next page content
                    next_page_response = requests.get(link, proxies=proxies, headers=headers)

                    # Check if the request to the next page was successful
                    if next_page_response.status_code == 200:
                        next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')

                        # Find the <div> with class 'desc'
                        desc_div = next_page_soup.find('div', class_='desc')

                        if desc_div:
                            description = desc_div.text.strip()  # Extract the text from the description div

                            # Write the processor name and description to the CSV file
                            csvwriter.writerow([processor_name, description])

                            print(f"Data for {processor_name} saved.")
                        else:
                            print(f"No description found for {processor_name}.")
                    else:
                        print(f"Failed to load page for {processor_name}. Status code: {next_page_response.status_code}")

                    # To avoid overwhelming the server with too many requests, pause for a moment
                    time.sleep(1)


    else:
        print("The UL element with class 'charlist' was not found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
