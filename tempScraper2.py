import re
import csv
import time  # Import time module for the sleep function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

# Path to your CSV file
csv_file_path = 'data.csv'

# Initialize the web driver (e.g., Chrome or Firefox)
# Make sure to specify the correct path to your WebDriver executable if it's not already in your PATH
driver = webdriver.Chrome()  # Change to your preferred browser and provide the path to the driver executable if needed
    

def open_url_with_parcel_id(parcel_id):
    # Construct the URL with the Parcel ID
    url = f"https://www.chesterfield.gov/828/Real-Estate-Assessment-Data#/Details/{parcel_id}"
    
    # Open the URL
    driver.get(url)

    #WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ownerName")))
    # Extract owner name
    try:
        owner_name = driver.find_element(By.ID, "ownerName").text
    except:
        owner_name = ""

    # Extract mailing address
    try:
        mailing_address = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "mailingAddress"))).text
    except:
        mailing_address = ""

    # Extract mailing address line 2
    try:
        mailing_address_line2 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "mailingAddressLine2"))).text
    except:
        mailing_address_line2 = ""

    # Extract mailing address line 3
    try:
        mailing_address_line3 = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "mailingAddressLine3"))).text
    except:
        mailing_address_line3 = ""

    # Extract ownership type
    try:
        ownership_type = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "ownershipType"))).text
    except:
        ownership_type = ""

    # Extract legal description
    try:
        price = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "larger-3"))).text
    except:
        price = ""

    # Extract acres
    try:
        acres = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, "acres"))).text
    except:
        acres = ""
    
    # Wait for the tabs element to be clickable, then click on it
    specific_css_selector = "#read-content > div.container.pa-0.fluid > div > div > div.v-tabs > div > div > div > div:nth-child(2)"
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, specific_css_selector))).click()

    # Wait for the initial element to be clickable and click it to open or expand the table
    initial_element_selector = "#tab_Tax > div > div.v-card__text > div > ul > li.flex.full-height.wrapper.xs12 > div > div.v-card__title.pr-4.lazy-content-medium-title.pt-3 > span > div > div > i"
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, initial_element_selector))).click()

    # Define the strings to search for
    search_strings = ["2023(2nd half): $", "2023(1st half): $", "2022(2nd half): $", "2022(1st half): $"]

    all_payments_valid = True

    # Loop through the search strings to find the elements and extract the data
    for s in search_strings:
        # Find the element containing the text
        element = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, f"//*[contains(text(),'{s}')]")))
        
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
        with open('output.csv', 'a', newline='') as csvfile:
                fieldnames = ["parcel_id", "owner_name", "mailing_address", "ownership_type", "price", "acres"]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                # Write headers if the file is empty
                if csvfile.tell() == 0:
                    writer.writeheader()

                # Write data
                writer.writerow({
                    "parcel_id": parcel_id,
                    "owner_name": owner_name,
                    "mailing_address": mailing_address + " " + mailing_address_line2 + " " + mailing_address_line3,
                    "ownership_type": ownership_type,
                    "price": price,
                    "acres": acres
                })
        
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



    

    # Here, you can add your code to extract data from the page or interact with the page further as needed


try:
    count = 0
    # Open and read the CSV file
    with open(csv_file_path, 'r') as data:
        mycsv = csv.reader(data)
        next(mycsv)  # Skip the header row if your CSV has one
        for row in mycsv:
            parcel_id = row[8]  # Assuming the Parcel ID is in the 9th column (index 8)
            open_url_with_parcel_id(parcel_id)
            count += 1
            print(f"You have searched through {count} parcels.")
            # Consider adding a short pause here if needed to avoid overwhelming the server or being blocked
            time.sleep(1)

except Exception as e:
    print("An error occurred:", str(e))

finally:
    # Close the web driver
    driver.quit()
