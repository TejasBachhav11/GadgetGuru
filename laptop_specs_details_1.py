from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time
import pandas as pd


# Set up Selenium options
options = Options()
options.add_argument('--headless')  # Run in headless mode
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('start-maximized')
options.add_argument('disable-infobars')
options.add_argument('--disable-extensions')
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Error Code - A0C03100EC7D0000]Automatic fallback to software WebGL has been deprecated. Please use the --enable-unsafe-swiftshader flag to opt in to lower security guarantees for trusted content.
options.add_argument("--enable-unsafe-swiftshader")



# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

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
        # time.sleep(3)

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

driver.quit()
