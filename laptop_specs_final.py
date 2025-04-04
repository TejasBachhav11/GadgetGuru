from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import pandas as pd

# Set up Selenium options
options = Options()
options.add_argument('--headless=new')  # Improved headless mode
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--disable-extensions')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--enable-webgl')
options.add_argument('--ignore-gpu-blacklist')
options.add_argument('--enable-unsafe-swiftshader')
options.add_argument('--disable-accelerated-2d-canvas')
options.add_argument('--disable-accelerated-video-decode')
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
)

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# Base URL pointing explicitly to the first page
base_url = "https://laptopmedia.com/in/specs/?page=1&size=n_100_n&filters%5B0%5D%5Bfield%5D=availability&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bto%5D=n_2_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bfrom%5D=n_1_n&filters%5B0%5D%5Bvalues%5D%5B0%5D%5Bname%5D=Show%20only%20available%20laptops&filters%5B0%5D%5Btype%5D=any"


count = 0
# Open CSV file to write the data
with open('laptop_links_all_pages.csv', 'w', newline='', encoding='utf-8') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Laptop Name', 'Link'])  # Write header row

    # Clear cookies before starting
    driver.delete_all_cookies()
    
    # Open the base URL
    driver.get(base_url)
    time.sleep(3)  # Allow page to load

    while True:
        try:
            # Extract the laptop data from the current page
            div = driver.find_element(By.CLASS_NAME, 'sui-layout-main-body')
            items = div.find_elements(By.TAG_NAME, 'li')

            for item in items:
                try:
                    a_tag = item.find_element(By.TAG_NAME, 'a')
                    laptop_name = item.text.strip()
                    link = a_tag.get_attribute('href')
                    csvwriter.writerow([laptop_name, link])
                    count+=1
                except Exception as e:
                    print(f"Skipping an item due to error: {e}")

            # Locate the pagination container
            pagination_container = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rc-pagination')))
            next_button = pagination_container.find_element(By.CLASS_NAME, 'rc-pagination-next')

            # Check if the "Next Page" button is disabled
            if 'rc-pagination-disabled' in next_button.get_attribute('class'):
                print("Reached the last page. Exiting.")
                print(f"Count of Laptops : {count}")
                break

            # Click the "Next Page" button
            next_button.click()
            time.sleep(2)  # Allow the next page to load
        except Exception as e:
            print(f"Error on page: {e}")
            break

    # Load the CSV containing links
    df = pd.read_csv('laptop_links_all_pages.csv')
    links = df['Link']
    i = 1
    # Open CSV file once to write data
    with open('laptop_details_1.csv', 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Name', 'Processor', 'Video Card', 'Display', 'Storage', 'RAM', 'Weight'])  # Write header row

        for link in links:
            base_url = link
            driver.get(base_url)
            time.sleep(1)

            try:
                # Extract Laptop Name
                name = driver.find_element(By.CLASS_NAME, 'text-3xl.font-extrabold.text-lm-darkBlue').text
                lst = [name]
                
                # Extract laptop specifications
                ul = driver.find_element(By.CLASS_NAME, 'lm-specs-table.text-lm-darkBlue.w-full.border-t.border-lm-borderBlue')
                items = ul.find_elements(By.TAG_NAME, 'li')

                for item in items:
                    lst.append(item.text.replace('"',''))

                # Write the extracted data to the CSV file
                csvwriter.writerow(lst)

            except Exception as e:
                print(f"Error on page {link}: {e}")

            print(f"Laptop : {i}")
            i+=1

# Close the browser
driver.quit()
