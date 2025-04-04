# import requests
# from bs4 import BeautifulSoup
# import time
# import re
# import csv

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }


# # URL of the page to scrape
# url = "https://laptopmedia.com/in/top-laptop-graphics-ranking/"

# proxies = {
#     'http': 'http://198.23.239.134:6540',
#     'https': 'http://198.23.239.134:6540'
# }

# # Send an HTTP GET request to fetch the page content
# response = requests.get(url, proxies=proxies, headers=headers)

# if response.status_code == 200:
#     # Parse the HTML content with BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     # Wait for a few seconds in case there are delays in loading the page
#     time.sleep(3)

#     #Find the <table> element with id 'all_lps'
#     table_elements = soup.find_all('tr')

#     txt = table_elements.get_text()

#     print(txt)

# else: 
#     print('error')
    



# import requests
# from bs4 import BeautifulSoup
# import time
# import csv

# # Headers for the request
# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }

# # Proxy configuration (optional)
# proxies = {
#     'http': 'http://198.23.239.134:6540',
#     'https': 'http://198.23.239.134:6540'
# }

# # URL of the page to scrape
# url = "https://laptopmedia.com/in/top-laptop-graphics-ranking/"

# # Send an HTTP GET request
# response = requests.get(url, proxies=proxies, headers=headers)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the HTML content with BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')
    
#     # Allow time for dynamic elements to load
#     time.sleep(3)

#     # Find the table with ID 'all_lps'
#     table_element = soup.find('table', id='all_lps')

#     if table_element:
#         # Extract all rows in the table
#         rows = table_element.find_all('tr')
        
#         # Prepare the CSV file
#         with open('gpu_rankings.csv', 'w', newline='', encoding='utf-8') as csvfile:
#             csvwriter = csv.writer(csvfile)
            
#             # Write the header row based on table structure
#             csvwriter.writerow(['Rank', 'GPU Name', 'Score', 'Category'])
            
#             # Loop through table rows, skipping the header
#             for row in rows[1:]:  # Skipping the header row
#                 cells = row.find_all('td')
                
#                 if len(cells) >= 4:  # Ensure the row has the expected number of columns
#                     rank = cells[0].get_text(strip=True)  # Rank
#                     gpu_name = cells[1].get_text(strip=True)  # GPU Name
#                     score = cells[2].get_text(strip=True).replace(',', '')  # Score (remove commas)
#                     category = cells[3].get_text(strip=True)  # Category
                    
#                     # Write row to CSV
#                     csvwriter.writerow([rank, gpu_name, score, category])
        
#         print("Data has been successfully written to gpu_rankings.csv")
#     else:
#         print("The table with ID 'all_lps' was not found.")
# else:
#     print(f"Failed to retrieve the page. Status code: {response.status_code}")



# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import csv
# import time

# # Configure Selenium WebDriver
# def setup_driver():
#     options = Options()
#     options.add_argument('--headless')  # Run in headless mode
#     options.add_argument('--disable-gpu')  # Disable GPU
#     options.add_argument('--no-sandbox')  # For environments like Linux
#     options.add_argument('--disable-dev-shm-usage')  # Overcome resource limits
#     options.add_argument('--window-size=1920,1080')  # Set a fixed window size
#     options.add_argument('start-maximized')  # Start with a maximized window
#     options.add_argument('log-level=3')  # Reduce logs

#     # Path to ChromeDriver
#     driver_path = "path/to/chromedriver"  # Update with your ChromeDriver path

#     return webdriver.Chrome(service=Service(driver_path), options=options)

# # Scrape data from the webpage
# def scrape_gpu_data():
#     url = "https://laptopmedia.com/in/top-laptop-graphics-ranking/"
#     driver = setup_driver()
#     try:
#         driver.get(url)  # Load the webpage
#         time.sleep(5)  # Wait for the page to load fully

#         # Find the table by ID 'all_lps'
#         table = driver.find_element(By.ID, 'all_lps')
#         rows = table.find_elements(By.TAG_NAME, 'tr')

#         if not rows:
#             print("No rows found in the table.")
#             return

#         # Prepare the CSV file
#         with open('gpu_rankings.csv', 'w', newline='', encoding='utf-8') as csvfile:
#             csvwriter = csv.writer(csvfile)
#             csvwriter.writerow(['Rank', 'GPU Name', 'Score', 'Category'])  # Write the header

#             # Extract data from each row
#             for row in rows[1:]:  # Skip the header row
#                 cells = row.find_elements(By.TAG_NAME, 'td')
#                 if len(cells) >= 4:
#                     rank = cells[0].text.strip()
#                     gpu_name = cells[1].text.strip()
#                     score = cells[2].text.strip().replace(',', '')  # Remove commas from scores
#                     category = cells[3].text.strip()

#                     # Write the row to the CSV
#                     csvwriter.writerow([rank, gpu_name, score, category])

#         print("Data has been successfully written to gpu_rankings.csv")

#     except Exception as e:
#         print(f"An error occurred: {e}")
#     finally:
#         driver.quit()  # Close the WebDriver

# # Run the scraper
# if __name__ == "__main__":
#     scrape_gpu_data()



# from playwright.sync_api import sync_playwright
# import csv

# def scrape_gpu_data():
#     url = "https://laptopmedia.com/in/top-laptop-graphics-ranking/"

#     with sync_playwright() as p:
#         # Launch the browser
#         browser = p.chromium.launch(headless=True)
#         context = browser.new_context()
#         page = context.new_page()

#         # Navigate to the URL
#         page.goto(url)
#         page.wait_for_timeout(5000)  # Wait 5 seconds for initial loading

#         # Scroll to the bottom to ensure all content is loaded
#         page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#         page.wait_for_timeout(5000)  # Wait for dynamic content to load

#         # Locate the table
#         try:
#             page.wait_for_selector("#all_lps", timeout=60000)  # Increased timeout
#             table = page.query_selector("#all_lps")

#             # Extract table rows
#             rows = table.query_selector_all("tr")
#             if not rows:
#                 print("No rows found in the table.")
#                 return

#             # Open a CSV file to write the data
#             with open('gpu_rankings.csv', 'w', newline='', encoding='utf-8') as csvfile:
#                 csvwriter = csv.writer(csvfile)
#                 csvwriter.writerow(['Rank', 'GPU Name', 'Score', 'Category'])  # Write header row

#                 for row in rows[1:]:  # Skip the header row
#                     cells = row.query_selector_all("td")
#                     if len(cells) >= 4:  # Ensure there are enough columns
#                         rank = cells[0].inner_text().strip()
#                         gpu_name = cells[1].inner_text().strip()
#                         score = cells[2].inner_text().strip().replace(",", "")  # Remove commas
#                         category = cells[3].inner_text().strip()

#                         # Write data to the CSV file
#                         csvwriter.writerow([rank, gpu_name, score, category])

#             print("Data has been successfully written to gpu_rankings.csv")
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             page.screenshot(path="error_screenshot.png")  # Debug screenshot
#         finally:
#             browser.close()

# # Run the scraper
# if __name__ == "__main__":
#     scrape_gpu_data()


# from playwright.sync_api import sync_playwright
# import csv

# def scrape_gpu_data():
#     url = "https://laptopmedia.com/in/top-laptop-graphics-ranking/"

#     with sync_playwright() as p:
#         # Launch the browser with proxy settings
#         proxy_settings = {
#             "server": "http://198.23.239.134:6540"
#         }
#         browser = p.chromium.launch(headless=True, proxy=proxy_settings)
#         context = browser.new_context()
#         page = context.new_page()

#         # Navigate to the URL
#         page.goto(url)
#         page.wait_for_timeout(5000)  # Wait 5 seconds for initial loading

#         # Scroll to the bottom to ensure all content is loaded
#         page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
#         page.wait_for_timeout(5000)  # Wait for dynamic content to load

#         # Locate the table
#         try:
#             page.wait_for_selector("#all_lps", timeout=60000)  # Increased timeout
#             table = page.query_selector("#all_lps")

#             # Extract table rows
#             rows = table.query_selector_all("tr")
#             if not rows:
#                 print("No rows found in the table.")
#                 return

#             # Open a CSV file to write the data
#             with open('gpu_rankings.csv', 'w', newline='', encoding='utf-8') as csvfile:
#                 csvwriter = csv.writer(csvfile)
#                 csvwriter.writerow(['Rank', 'GPU Name', 'Score', 'Category'])  # Write header row

#                 for row in rows[1:]:  # Skip the header row
#                     cells = row.query_selector_all("td")
#                     if len(cells) >= 4:  # Ensure there are enough columns
#                         rank = cells[0].inner_text().strip()
#                         gpu_name = cells[1].inner_text().strip()
#                         score = cells[2].inner_text().strip().replace(",", "")  # Remove commas
#                         category = cells[3].inner_text().strip()

#                         # Write data to the CSV file
#                         csvwriter.writerow([rank, gpu_name, score, category])

#             print("Data has been successfully written to gpu_rankings.csv")
#         except Exception as e:
#             print(f"An error occurred: {e}")
#             page.screenshot(path="error_screenshot.png")  # Debug screenshot
#         finally:
#             browser.close()

# # Run the scraper
# if __name__ == "__main__":
#     scrape_gpu_data()



from bs4 import BeautifulSoup
import requests
import csv

def scrape_gpu_data():
    url = "https://laptopmedia.com/in/top-laptop-graphics-ranking/"

    # Fetch the webpage content
    # headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0'
    # }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://laptopmedia.com/',
    'Upgrade-Insecure-Requests': '1'
    }

    proxies = {
    'http': 'http://207.244.217.165:6712',
    'https': 'http://207.244.217.165:6712'
    }

    response = requests.get(url,proxies = proxies,   headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the table
        table = soup.find("table", id="all_lps")
        if not table:
            print("Table not found!")
            return

        # Find all rows in the table
        rows = table.find("tbody").find_all("tr")

        # Open a CSV file to save the data
        with open("gpu_rankings.csv", "w", newline="", encoding="utf-8") as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write the header row
            csvwriter.writerow(['Rank', 'GPU Name', '3DMark Score', 'Performance Difference', 'Prices', 'Price Difference'])

            for row in rows:
                # Get all table cells in the row
                cells = row.find_all("td")
                if len(cells) >= 6:  # Ensure there are enough columns
                    rank = cells[0].text.strip()  # Rank
                    gpu_name = cells[1].text.strip()  # GPU Name
                    score = cells[2].text.strip()  # 3DMark Score
                    performance_difference = cells[3].text.strip()  # Performance Difference
                    prices = cells[4].text.strip()  # Prices
                    price_difference = cells[5].text.strip()  # Price Difference

                    # Write the data to CSV
                    csvwriter.writerow([rank, gpu_name, score, performance_difference, prices, price_difference])

        print("Data has been successfully written to gpu_rankings.csv")
    else:
        print(f"Failed to fetch the webpage. Status code: {response.status_code}")

# Run the scraper
if __name__ == "__main__":
    scrape_gpu_data()
