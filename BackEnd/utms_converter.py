import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    service = Service('/Users/arnau1146/Developer/chromedriver-mac-arm64/chromedriver')  # Update with the correct path to your chromedriver
    return webdriver.Chrome(service=service, options=chrome_options)

def convert_utm_to_latlon(driver, utm_este, utm_norte):
    driver.get("https://www.padeepro.com/converterutm.html")

    wait = WebDriverWait(driver, 20)  # Increased wait time to 20 seconds

    try:
        utm_e_box1 = wait.until(EC.element_to_be_clickable((By.ID, "UTMeBox1")))
        utm_e_box1.clear()
        utm_e_box1.send_keys(utm_norte)

        utm_e_box2 = wait.until(EC.element_to_be_clickable((By.ID, "UTMeBox2")))
        utm_e_box2.clear()
        utm_e_box2.send_keys(utm_este)

        convert_button = wait.until(EC.element_to_be_clickable((By.ID, "btnConvert")))
        convert_button.click()

        lat = wait.until(EC.visibility_of_element_located((By.ID, "latResultId"))).text
        lon = wait.until(EC.visibility_of_element_located((By.ID, "lonResultId"))).text

        return lat, lon
    except Exception as e:
        print(f"Exception: {e}")
        if hasattr(e, 'msg'):
            print(f"Message: {e.msg}")
        if hasattr(e, 'screen'):
            print(f"Screen: {e.screen}")
        if hasattr(e, 'stacktrace'):
            print(f"Stacktrace: {e.stacktrace}")
        return None, None

def process_item(driver, item):
    utm_este = item.get('longitud')
    utm_norte = item.get('latitud')
    if utm_este and utm_norte:
        lat, lon = convert_utm_to_latlon(driver, utm_este, utm_norte)
        if lat and lon:
            result = {
                'nomMonumento': item.get('nomMonumento'),
                'lat': lat,
                'lon': lon
            }
            print(result)
            return result
    return None

def process_json(json_path):
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return []

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    driver = create_driver()
    results = []
    for item in data:
        result = process_item(driver, item)
        if result:
            results.append(result)
    driver.quit()

    return results

# Ruta al archivo JSON procesado
json_path = '../Resultados/CSVtoJSON_con_coords.json'
results = process_json(json_path)

# Imprimir los resultados
for result in results:
    print(result)