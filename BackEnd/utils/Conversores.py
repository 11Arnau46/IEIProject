import json
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json
import Coords_converter

def convertir_coordenadas_utm(ruta_json_entrada, ruta_json_salida):
    # Cargar el archivo JSON
    with open(ruta_json_entrada, "r", encoding="utf-8") as file:
        monumentos = json.load(file)

    # Actualiza los datos del JSON con coordenadas convertidas
    for monumento in monumentos:
        if monumento["latitud"] and monumento["longitud"]:
            print(f"Convirtiendo coordenadas UTM para {monumento['nomMonumento']}...")

            try:
                # Convertir las coordenadas UTM a latitud y longitud
                lat, lon = Coords_converter.convert_utm(float(monumento["latitud"]), float(monumento["longitud"]))
                
                if lat and lon:
                    monumento["latitud"] = lat
                    monumento["longitud"] = lon
            except Exception as e:
                print(f"Error al convertir las coordenadas para {monumento['nomMonumento']}: {e}")

    # Guardar el archivo actualizado
    with open(ruta_json_salida, "w", encoding="utf-8") as file:
        json.dump(monumentos, file, ensure_ascii=False, indent=4)

    print(f"Archivo actualizado guardado en {ruta_json_salida}.")
