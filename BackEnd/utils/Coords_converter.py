from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


import time

""" def convert_utm(latitud, longitud):
    # Inicializa el navegador
    driver = webdriver.Chrome()  # Asegúrate de que 'chromedriver' esté en tu PATH
    driver.get("https://www.ign.es/web/calculadora-geodesica")

    # Espera a que la página cargue
    time.sleep(5)

    # Encuentra y activa el radio button para introducir coordenadas en UTM 
    element = driver.findElement(By.id("radioButton1"))
    wait = WebDriverWait(driver, 120)
    wait.until(ExpectedConditions.elementToBeClickable(element))

    element.click()

    time.sleep(3)

    # Encuentra el campo x metros e introduce el valor de latitud
    driver.find_element(By.ID, "datacoord1").clear()
    driver.find_element(By.ID, "datacoord1").send_keys(latitud)  # Envía el valor de latitud

    # Encuentra el campo y metros e introduce el valor de longitud
    driver.find_element(By.ID, "datacoord2").clear()
    driver.find_element(By.ID, "datacoord2").send_keys(longitud)  # Envía el valor de longitud

    # Encuentra y activa el botón de calcular
    driver.find_element(By.ID, "trd_calc").click()

    # Espera un momento para que se procese la conversión
    time.sleep(5)

    # Obtiene la latitud y longitud en grados
    lat = driver.find_element(By.ID, "txt_etrs89_latgd").text  # Cambia el ID según el resultado de latitud
    lon = driver.find_element(By.ID, "txt_etrs89_longd").text  # Cambia el ID según el resultado de longitud

    # Cierra el navegador
    driver.quit()

    return lat, lon """
class CoordsConverter:
    @staticmethod
    def convert_utm(latitud, longitud):
        opciones = Options()
        opciones.add_argument("--headless")  # Habilita el modo headless (sin interfaz gráfica)

        # Inicializa el navegador con las opciones configuradas
        driver = webdriver.Chrome(options=opciones)  # Asegúrate de que 'chromedriver' esté en tu PATH
        driver.get("https://www.ign.es/web/calculadora-geodesica")

        # Espera a que la página cargue
        #time.sleep(5)

        # Encuentra y activa el radio button para introducir coordenadas en UTM 
        # Localiza el radio button por ID
        radio_button = driver.find_element(By.ID, "utm")

        # Usar JavaScript para desplazar el elemento a la vista
        driver.execute_script("arguments[0].scrollIntoView(true);", radio_button)

        # Usar ActionChains para mover el cursor al elemento y hacer clic
        actions = ActionChains(driver)
        actions.move_to_element(radio_button).click().perform()

        #time.sleep(3)

        # Encuentra el campo x metros e introduce el valor de latitud
        driver.find_element(By.ID, "datacoord1").clear()
        driver.find_element(By.ID, "datacoord1").send_keys(latitud)  # Envía el valor de latitud

        # Encuentra el campo y metros e introduce el valor de longitud
        driver.find_element(By.ID, "datacoord2").clear()
        driver.find_element(By.ID, "datacoord2").send_keys(longitud)  # Envía el valor de longitud

        # Encuentra y activa el botón de calcular
        driver.find_element(By.ID, "trd_calc").click()

        # Espera un momento para que se procese la conversión
        time.sleep(3)

        # Obtiene la latitud y longitud en grados
        lat = driver.find_element(By.ID, "txt_etrs89_latgd").get_attribute("value")
        lon = driver.find_element(By.ID, "txt_etrs89_longd").get_attribute("value")

        #print(lat)
        #print(lon)

        # Cierra el navegador
        driver.quit()

        return lat, lon