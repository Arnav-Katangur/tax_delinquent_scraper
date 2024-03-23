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


def check_text_exists(text):
    try:
        # This looks for an element that contains the exact text
        # It uses XPath's contains() function to search for the text within any element in the webpage
        driver.find_element(By.XPATH, f"//*[contains(text(), '{text}')]")
        return True
    except NoSuchElementException:
        return False
    

def open_url_with_parcel_id(parcel_id):
    # Construct the URL with the Parcel ID
    url = f"https://www.chesterfield.gov/828/Real-Estate-Assessment-Data#/Details/{parcel_id}"
    
    # Open the URL
    driver.get(url)
    
    # Wait for the tabs element to be clickable, then click on it
    specific_css_selector = "#read-content > div.container.pa-0.fluid > div > div > div.v-tabs > div > div > div > div:nth-child(2)"
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, specific_css_selector))).click()

    # Wait for the initial element to be clickable and click it to open or expand the table
    initial_element_selector = "#tab_Tax > div > div.v-card__text > div > ul > li.flex.full-height.wrapper.xs12 > div > div.v-card__title.pr-4.lazy-content-medium-title.pt-3 > span > div > div > i"
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, initial_element_selector))).click()

    time.sleep(5)

    # Define the strings to search for
    search_strings = ["2023(2nd half): $", "2023(1st half): $", "2022(2nd half): $", "2022(1st half): $"]

    # Loop through the search strings to find the elements and extract the data
    for s in search_strings:
        # Find the element containing the text
        element = driver.find_element(By.XPATH, f"//*[contains(text(),'{s}')]")
        
        # Extract the full text from the element
        full_text = element.text
        
        # Use regular expression to extract the amount
        match = re.search(r'\$([\d,.]+)', full_text)
        if match:
            amount = match.group(1)
            print(f"{s}{amount}")
        else:
            print(f"Amount not found for '{s}'.")



    # Wait for about 10 seconds as a placeholder
    time.sleep(10)

    # Here, you can add your code to extract data from the page or interact with the page further as needed


try:
    # Open and read the CSV file
    with open(csv_file_path, 'r') as data:
        mycsv = csv.reader(data)
        next(mycsv)  # Skip the header row if your CSV has one
        for row in mycsv:
            parcel_id = row[8]  # Assuming the Parcel ID is in the 9th column (index 8)
            open_url_with_parcel_id(parcel_id)
            # Consider adding a short pause here if needed to avoid overwhelming the server or being blocked
            time.sleep(10)

except Exception as e:
    print("An error occurred:", str(e))

finally:
    # Close the web driver
    driver.quit()
