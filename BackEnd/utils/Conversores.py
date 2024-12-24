import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def convertir_coordenadas_utm(ruta_json_entrada, ruta_json_salida):
    # Cargar el archivo JSON
    with open(ruta_json_entrada, "r", encoding="utf-8") as file:
        monumentos = json.load(file)

    # Configurar Selenium para usar el navegador
    driver = webdriver.Chrome()  # Asegúrate de tener el controlador adecuado para tu navegador

    # Actualiza los datos del JSON
    for monumento in monumentos:
        if monumento["latitud"] and monumento["longitud"]:
            print(f"Convirtiendo coordenadas UTM para {monumento['nomMonumento']}...")
            
            # Acceder a la calculadora geodésica
            driver.get("https://www.ign.es/web/calculadora-geodesica")

            # Espera a que la página cargue
            time.sleep(2)  # Puedes ajustar el tiempo de espera según la velocidad de tu conexión

            # Encontrar los campos de latitud y longitud en la página
            lat_input = driver.find_element(By.ID, "utmLat")
            lon_input = driver.find_element(By.ID, "utmLon")

            # Introducir las coordenadas UTM
            lat_input.clear()
            lat_input.send_keys(str(monumento["latitud"]))
            lon_input.clear()
            lon_input.send_keys(str(monumento["longitud"]))

            # Hacer clic en el botón para convertir
            convert_button = driver.find_element(By.ID, "botonCalcular")
            convert_button.click()

            # Espera a que los resultados aparezcan
            time.sleep(2)

            # Obtener las coordenadas convertidas
            try:
                lat_result = driver.find_element(By.ID, "valorLatitud").text
                lon_result = driver.find_element(By.ID, "valorLongitud").text
                monumento["latitud"] = lat_result
                monumento["longitud"] = lon_result
            except Exception as e:
                print(f"Error al obtener las coordenadas para {monumento['nomMonumento']}: {e}")

    # Guardar el archivo actualizado
    with open(ruta_json_salida, "w", encoding="utf-8") as file:
        json.dump(monumentos, file, ensure_ascii=False, indent=4)

    # Cerrar el navegador
    driver.quit()

    print(f"Archivo actualizado guardado en {ruta_json_salida}.")
