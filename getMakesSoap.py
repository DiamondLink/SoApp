from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException


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

dict_car = {}


# Navigate to the webpage
driver.get('http://10.7.172.9:8181/#/ajoutTicket')
time.sleep(5)
select_element = driver.find_element_by_css_selector("[ng-model='piece.marque']")
select = Select(select_element)
options = select.options
for option in options:
    if "Choisir" in option.text:
        continue
    modeles = {}
    option.click()
    select_element2 = driver.find_element_by_css_selector("[ng-model='piece.modele']")
    select2 = Select(select_element2)
    options2 = select2.options
    for option2 in options2:
        if "Choisir" in option2.text:
            continue
        phases = []
        option2.click()
        try:
            select_element3 = driver.find_element_by_css_selector("[ng-model='piece.phase']")
            select3 = Select(select_element3)
            options3 = select3.options
            for option3 in options3:
                if "Choisir" in option3.text:
                    continue
                phases.append(option3.text)
        except NoSuchElementException:
            pass
        except Exception as e:
            print(str(e))
        
        modeles[option2.text] = phases
    dict_car[option.text] = modeles
    

driver.quit()

with open("modeles.json", "w") as file:
    # Convert the dictionary to a JSON string
    json_string = json.dumps(dict_car, indent=4)
    
    # Write the JSON string to the file
    file.write(json_string)
