from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import logging

PRODUCT_URL = "YOUR_PRODUCT_URL"
POSTAL_CODE = "YOUR_POSTAL"  
CHECK_INTERVAL = 60 


logging.basicConfig(filename='availability_check.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_availability(driver):
    driver.get(PRODUCT_URL)
    wait = WebDriverWait(driver, 20)  

    try:
        check_availability_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-autom="productLocatorTriggerLink"]')))
        check_availability_button.click()
        postal_code_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-autom="zipCode"]')))        
        actions = ActionChains(driver)
        actions.click(postal_code_input)
        actions.send_keys(POSTAL_CODE)
        actions.perform()

        time.sleep(3)
        
        postal_code_input.send_keys(Keys.RETURN)        
        availability_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'rf-productlocator-storeoption')))
        availability_text = availability_element.text
        print(f"Availability status: {availability_text}")
        logging.info(f"Availability status: {availability_text}")
        
        if "Available Today" in availability_text or "Available Tomorrow" in availability_text:
            print("In stock! Keeping the page open.")
            logging.info("In stock! Keeping the page open.")
            return True
        else:
            print("Out of stock.")
            logging.info("Out of stock.")
            return False
        
    except Exception as e:
        print(f"Error checking availability: {e}")
        logging.error(f"Error checking availability: {e}")
        with open("error_page_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)        
        driver.save_screenshot("error_screenshot.png")       
        return None

def main():
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")  
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        while True:
            in_stock = check_availability(driver)
            if in_stock:
                print("Stock found, keeping the page open.")
                logging.info("Stock found, keeping the page open.")
            else:
                print("No stock, closing the browser and waiting.")
                logging.info("No stock, closing the browser and waiting.")
                driver.quit()  
                time.sleep(CHECK_INTERVAL)
                driver = webdriver.Chrome(options=chrome_options)    
    except KeyboardInterrupt:
        print("Script terminated.")    
    finally:
        try:
            driver.quit()
        except:
            pass
        
if __name__ == "__main__":
    main()
