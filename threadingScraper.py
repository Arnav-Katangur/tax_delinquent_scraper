import csv
import re
import threading
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Set options for WebDriver
options = Options()
options.headless = True  # Headless mode
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--disable-images")  # Disable images

# Function to handle each parcel's data extraction
def handle_parcel(parcel_id):
    # Local driver for thread
    local_driver = webdriver.Chrome(options=options)
    local_driver.set_page_load_timeout(10)
    try:
        local_driver.get(f'https://www.chesterfield.gov/828/Real-Estate-Assessment-Data#/Details/{parcel_id}')
        
        # Add all the necessary waits and data extraction logic here
        WebDriverWait(local_driver, 10).until(EC.visibility_of_element_located((By.ID, "ownerName")))
        owner_name = local_driver.find_element(By.ID, "ownerName").text
        mailing_address = local_driver.find_element(By.ID, "mailingAddress").text
        mailing_address_line2 = local_driver.find_element(By.ID, "mailingAddressLine2").text
        mailing_address_line3 = local_driver.find_element(By.ID, "mailingAddressLine3").text
        ownership_type = local_driver.find_element(By.ID, "ownershipType").text
        price = local_driver.find_element(By.CLASS_NAME, "larger-3").text
        acres = local_driver.find_element(By.ID, "acres").text
        
        # Wait for the tabs element to be clickable, then click on it
        specific_css_selector = "#read-content > div.container.pa-0.fluid > div > div > div.v-tabs > div > div > div > div:nth-child(2)"
        WebDriverWait(local_driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, specific_css_selector))).click()

        # Wait for the initial element to be clickable and click it to open or expand the table
        initial_element_selector = "#tab_Tax > div > div.v-card__text > div > ul > li.flex.full-height.wrapper.xs12 > div > div.v-card__title.pr-4.lazy-content-medium-title.pt-3 > span > div > div > i"
        WebDriverWait(local_driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, initial_element_selector))).click()

        # Define the strings to search for
        search_strings = ["2023(2nd half): $", "2023(1st half): $", "2022(2nd half): $", "2022(1st half): $"]

        all_payments_valid = True

        # Loop through the search strings to find the elements and extract the data
        for s in search_strings:
            # Find the element containing the text
            element = WebDriverWait(local_driver, 20).until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(),'{s}')]")))
            
            # Extract the full text from the element
            full_text = element.text
            
            # Use regular expression to extract the amount
            match = re.search(r'\$([\d,.]+)', full_text)
            if match:
                amount = float(match.group(1).replace(',', ''))
                # Check if the amount is greater than 0
                if amount <= 0:
                    all_payments_valid = False
                    break
            else:
                # If any amount is not found, it's invalid
                all_payments_valid = False
                break

        if all_payments_valid:
            # Extract additional information
            print(f"{parcel_id} is valid")
            print(f"Owner Name: {owner_name}")
            print(f"Mailing Address: {mailing_address} ")
            print(f"Mailing Address Line 2: {mailing_address_line2}")
            print(f"Mailing Address Line 3: {mailing_address_line3}")
            print(f"Ownership Type: {ownership_type}")
            print(f"Price: {price}")
            print(f"Acres: {acres}")
        else:
            print(f"{parcel_id} is not valid")
        # ...

    except Exception as e:
        print(f"An error occurred with parcel {parcel_id}: {e}")
    finally:
        local_driver.quit()

# Load parcel IDs from the CSV file
parcel_ids = []
with open('data.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header
    for row in reader:
        if row:  # Add check to ensure row is not empty
            parcel_id = row[8]  # Assuming the Parcel ID is in the 9th column
            parcel_ids.append(parcel_id)

# List to hold threads
threads = []

# Start threads
for parcel_id in parcel_ids:
    thread = threading.Thread(target=handle_parcel, args=(parcel_id,))
    threads.append(thread)
    thread.start()

    # Optional: Implement some form of rate limiting to avoid hitting the website too hard
    time.sleep(1)

# Wait for all threads to complete
for thread in threads:
    thread.join()

print("Data extraction complete.")