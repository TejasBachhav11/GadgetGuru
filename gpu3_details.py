import requests
from bs4 import BeautifulSoup
import time
import re
import csv

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# URL of the Page
url = "https://www.videocardbenchmark.net/high_end_gpus.html"

proxies = {
    'http' : 'http://207.244.217.165:6712',
    'https' : 'http://207.244.217.165:6712'
}

# Send HTTP GET request to fetch the page content
response = requests.get(url, proxies = proxies, headers = headers)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Waiting for Page to load
    time.sleep(3)

    # Find the <ul> element with class 'chartlist'
    ul_element = soup.find('ul', class_= 'chartlist')

    if ul_element:
        # Get all <li> elements in <ul>
        list_items = ul_element.find_all('li')

        for item in list_items:
            # Find anchor tag inside the <li> element
            a_tag = item.find('a')

            if a_tag and a_tag['href']:
                # Get the processor name from the <a> tag
                gpu_name = a_tag.text.strip()
                # Get the link to the next page
                link = a_tag['href']
                
                # If the link is relative, prepend the base URL
                if not link.startswith('http'):
                    link = "https://www.videocardbenchmark.net/" + link

                next_page_response = requests.get(link, proxies=proxies, headers=headers)

                if(next_page_response.status_code ==200):
                    next_page_soup = BeautifulSoup(next_page_response.content, 'html.parser')

                    desc_div = next_page_soup.find('div', class_='desc')

                if desc_div :
                    # Extract text from the description div
                    description = desc_div.text.strip()

                    print(gpu_name)
                    print(description)
                    print('\n')

                else :
                    print(f"No description for {gpu_name}" )

            else:
                print(f"Failed to load page for {gpu_name}. Status code: {next_page_response.status_code}")
            
            # To avoid overwhelming the server with too many requests, pause for a moment
            time.sleep(1)

    else:
        print("The UL element with class 'charlist' was not found.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")