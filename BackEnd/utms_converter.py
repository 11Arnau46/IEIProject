from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def convert_utm(utm_este, utm_norte):
    # Inicializa el navegador
    driver = webdriver.Chrome()  # Asegúrate de que 'chromedriver' esté en tu PATH
    driver.get("https://www.padeepro.com/converterutm.html")

    # Espera a que la página cargue
    time.sleep(2)

    # Encuentra el campo UTMESTE y UTMNORTE e introduce los valores
    driver.find_element(By.ID, "UTMeBox1").clear()
    driver.find_element(By.ID, "UTMeBox1").send_keys(utm_norte)  # Envía el valor de UTMNORTE

    driver.find_element(By.ID, "UTMeBox2").clear()
    driver.find_element(By.ID, "UTMeBox2").send_keys(utm_este)  # Envía el valor de UTMESTE

    # Simula el envío del formulario
    driver.find_element(By.ID, "btnConvert").click()  # Ajusta el ID del botón según corresponda

    # Espera un momento para que se procese la conversión
    time.sleep(5)

    # Obtén el resultado (ajusta el selector según el HTML de la página)
    lat = driver.find_element(By.ID, "latResultId").text  # Cambia el ID según el resultado de latitud
    lon = driver.find_element(By.ID, "lonResultId").text  # Cambia el ID según el resultado de longitud

    # Cierra el navegador
    driver.quit()

    return lat, lon
