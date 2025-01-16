import sys
import os
import pandas as pd
import json
from pathlib import Path

import requests

# Define the root project directory and add it to Python path
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from BackEnd.config.paths import INPUT_CSV_PATH
from BackEnd.utils.Filtros import *
from BackEnd.utils.Otros import *
from BackEnd.utils.Conversores import convertir_coordenadas_utm
from BackEnd.utils.Location_Finder import LocationFinder
from BackEnd.utils.Coords_converter import CoordsConverter

def get_datos():
    # Obtener la ruta del directorio raíz y actual
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

    # Crear la ruta completa hacia el archivo JSON procesado
    path = os.path.abspath(os.path.join(BASE_DIR, 'Resultados', 'CSVtoJSON_Corregido.json'))

    # Leer el archivo JSON con la codificación utf-8
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data

def get_datos_fuente():
    """
    Hace una solicitud a la API y guarda la respuesta como un objeto JSON.

    Retorna:
        dict: Los datos procesados como un diccionario Python.
    """
    api_url = "http://localhost:8083/wrapperCSV/execute"

    try:
        # Realizar la solicitud a la API
        response = requests.post(api_url)

        # Verificar si la respuesta es exitosa
        response.raise_for_status()

        # Procesar el contenido de la respuesta como JSON
        data = response.json()

        # Retornar el objeto JSON procesado
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud a la API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al procesar la respuesta como JSON: {e}")
        return None
    
def process_json():
    # Configurar la fuente de datos y los loggers
    data_source = "csv"
    set_data_source(data_source)
    setup_loggers(data_source)

    # Obtener los datos desde la API
    data_fuente = get_datos_fuente()
    if data_fuente is None:
        print("No se pudieron obtener datos de la fuente.")
        return

    # Diccionario para almacenar los datos extraídos
    data = { 
        'nomMonumento': [], 
        'tipoMonumento': [], 
        'direccion': [], 
        'codigo_postal': [], 
        'longitud': [], 
        'latitud': [], 
        'descripcion': [], 
        'nomLocalidad': [], 
        'nomProvincia': [] 
    }

    seen_monuments = set()

    # Función para extraer los datos del JSON
    def extraer_datos_json(item, seen_monuments):
        nomMonumento = item['DENOMINACION']
        tipoMonumento = get_tipo_monumento(nomMonumento)
        direccion = pd.NA
        codigo_postal = pd.NA
        latitud = item['UTMNORTE'] if item['UTMNORTE'] else pd.NA
        longitud = item['UTMESTE'] if item['UTMESTE'] else pd.NA
        descripcion = item['CLASIFICACION']
        nomLocalidad = item['MUNICIPIO'] if item['MUNICIPIO'] else pd.NA
        nomProvincia = item['PROVINCIA'] if item['PROVINCIA'] else pd.NA

        # Validar utilizando la función de filtros
        if not aplicar_filtros("CSV", nomMonumento, nomProvincia, nomLocalidad, codigo_postal, latitud, longitud, direccion, seen_monuments):
            return None  # Si no pasa las validaciones, omitimos el monumento

        # Agregar a 'seen_monuments'
        seen_monuments.add(nomMonumento)

        return {
            'nomMonumento': nomMonumento,
            'tipoMonumento': tipoMonumento,
            'direccion': direccion,
            'codigo_postal': codigo_postal,
            'latitud': latitud,
            'longitud': longitud,
            'descripcion': descripcion,
            'nomLocalidad': nomLocalidad,
            'nomProvincia': nomProvincia
        }

    # Extraer la información de cada item en la respuesta JSON
    for item in data_fuente:
        extracted_data = extraer_datos_json(item, seen_monuments)
        if extracted_data is not None:  # Solo agregar si los datos no son None
            for key, value in extracted_data.items():
                data[key].append(value)

    # Crear DataFrame con los datos extraídos
    df_result = pd.DataFrame(data)

    # Aplicar filtros estandarizados al DataFrame
    df_result = aplicar_correcciones(df_result)

    # Dividir los datos en aquellos con coordenadas y sin coordenadas y filtrar monumentos repetidos 
    df_con_coords, df_sin_coords = procesar_datos(df_result, 'csvtojson')

    # Convertir coordenadas
    ruta_json_entrada = root_dir / 'Resultados' / 'CSVtoJSON_con_coords.json'
    ruta_json_salida = root_dir / 'Resultados' / 'CSVtoJSON_Corregido.json'

    # Print the paths for debugging purposes
    print(f"Path to input JSON: {ruta_json_entrada}")
    print(f"Path to output JSON: {ruta_json_salida}")

    # Verificar si el archivo de entrada existe
    if not ruta_json_entrada.exists():
        print(f"Input file does not exist: {ruta_json_entrada}")
    else:
        with open(ruta_json_entrada, "r", encoding="utf-8") as file:
            monumentos = json.load(file)

    convertir_coordenadas_utm(ruta_json_entrada, ruta_json_salida)

    process_and_save_json(ruta_json_salida)

    # Cargar los datos actualizados
    with open(ruta_json_salida, 'r', encoding='utf-8') as f:
        datos_actualizados = json.load(f)

    # Crear nuevo DataFrame con los datos actualizados
    df_result = pd.DataFrame(datos_actualizados)

    # Segunda validación después de Location Finder
    registros_validos = []
    for _, row in df_result.iterrows():
        if aplicar_filtros("CSV", row['nomMonumento'], row['nomProvincia'], row['nomLocalidad'], 
                        row['codigo_postal'], row['latitud'], row['longitud'], row['direccion'], 
                        set(), pasadoPorLocationFinder=True):
            registros_validos.append(row)

    # Actualizar el DataFrame con solo los registros válidos
    df_result = pd.DataFrame(registros_validos)

    # Guardar los resultados finales validados
    df_result.to_json(ruta_json_salida, orient='records', force_ascii=False)

    log_statistics()

# Check if the script is being run directly
if __name__ == "__main__":
    process_json()