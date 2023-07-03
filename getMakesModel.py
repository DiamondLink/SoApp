from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

ublock_origin_path = 'C://Users//Baptiste//Downloads//uBlock-Origin.crx'
chrome_options = Options()
chrome_options.add_extension(ublock_origin_path)
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("—disable-gpu")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")
#chrome_options.add_argument("--start-maximized")
#chrome_options.add_argument('--headless')
# Set up the Selenium webdriver
driver = webdriver.Chrome(service=Service('chromedriver'), options=chrome_options)




# Navigate to the webpage
driver.get('https://www.netcarshow.com/')

time.sleep(5)


ul_elements = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'lst')))

car_dict = {}

# Iterate over each <ul> element and extract the text from the <a> tags
for ul_element in ul_elements:
    a_elements = ul_element.find_elements(By.TAG_NAME, 'a')
    for element in a_elements:
        original_window = driver.current_window_handle

        models = []
        name = element.text
        element.send_keys(Keys.CONTROL + Keys.RETURN)

        time.sleep(2)
        driver.switch_to.window(driver.window_handles[-1])

        ul_elements2 = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'lst')))
        for ul_element2 in ul_elements2:
            a_elements2 = ul_element2.find_elements(By.TAG_NAME, 'a')

            for element2 in a_elements2:
                models.append(element2.text)
        car_dict[name] = models
        driver.close()
        driver.switch_to.window(original_window)

        time.sleep(1)

        with open("modeles.json", "w") as file:
    # Convert the dictionary to a JSON string
            json_string = json.dumps(car_dict, indent=4)
    
    # Write the JSON string to the file
            file.write(json_string)




# Close the webdriver
driver.quit()