import json
import pandas as pd
import os
from pathlib import Path
import sys
import requests

# Define the root project directory and add it to Python path
root_dir = Path(__file__).resolve().parents[2]
sys.path.append(str(root_dir))

from BackEnd.utils.Filtros import get_tipo_monumento, clean_html_text, procesar_datos
from BackEnd.utils.Otros import *
from BackEnd.config.paths import INPUT_JSON_PATH

def get_datos():
    # Obtener la ruta del directorio raíz y actual
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

    # Crear la ruta completa hacia "Fuente_de_datos/Final/vcl.csv"
    path = os.path.abspath(os.path.join(BASE_DIR, 'Resultados', 'XMLtoJSON_con_coords.json'))
  

    # Leer el archivo XML con la codificación utf-8
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    return data


def get_datos_fuente():
    """
    Hace una solicitud a la API y guarda la respuesta como un objeto JSON.

    Parámetros:
        api_url (str): La URL de la API que se va a consultar.

    Retorna:
        dict: Los datos procesados como un diccionario Python.
    """
    api_url = "http://localhost:8081/wrapperXML/execute"

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
    data_source = "xml"
    set_data_source(data_source)
    setup_loggers(data_source)

    data_json = get_datos_fuente()

    # Extraer la lista de monumentos
    monumentos = data_json.get("monumentos", {}).get("monumento", [])
    num_monumentos = len(monumentos)
    
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

    # Extraer datos de cada monumento
    for monumento in monumentos:
        nomMonumento = monumento.get("nombre", pd.NA)
        tipoMonumento = get_tipo_monumento(monumento.get("tipoMonumento", pd.NA))
        direccion = monumento.get("calle", pd.NA)
        codigo_postal = monumento.get("codigoPostal", pd.NA)
        coordenadas = monumento.get("coordenadas", {})
        longitud = coordenadas.get("longitud", pd.NA)
        latitud = coordenadas.get("latitud", pd.NA)
        descripcion = clean_html_text(monumento.get("Descripcion", pd.NA))
        poblacion = monumento.get("poblacion", {})
        nomLocalidad = poblacion.get("localidad", pd.NA)
        nomProvincia = poblacion.get("provincia", pd.NA)

        # Validar utilizando los filtros
        if not aplicar_filtros("XML", nomMonumento, nomProvincia, nomLocalidad, codigo_postal, latitud, longitud, direccion, seen_monuments):
            continue  # Si no pasa las validaciones, omitir el monumento

        # Agregar a 'seen_monuments'
        seen_monuments.add(nomMonumento)

        # Agregar los datos al diccionario
        data['nomMonumento'].append(nomMonumento)
        data['tipoMonumento'].append(tipoMonumento)
        data['direccion'].append(direccion)
        data['codigo_postal'].append(codigo_postal)
        data['longitud'].append(longitud)
        data['latitud'].append(latitud)
        data['descripcion'].append(descripcion)
        data['nomLocalidad'].append(nomLocalidad)
        data['nomProvincia'].append(nomProvincia)

    # Crear DataFrame
    df_result = pd.DataFrame(data)

    # Aplicar correcciones y procesar datos
    df_result = aplicar_correcciones(df_result)
    df_con_coords, df_sin_coords = procesar_datos(df_result, 'xmltojson')

    # Definir ruta de salida
    root_dir = Path(__file__).resolve().parents[2]
    ruta_json_salida = root_dir / 'Resultados' / 'XMLtoJSON_con_coords.json'

    # Print the path for debugging purposes
    print(f"Path to output JSON: {ruta_json_salida}")

    process_and_save_json(ruta_json_salida)

    # Cargar los datos actualizados
    with open(ruta_json_salida, 'r', encoding='utf-8') as f:
        datos_actualizados = json.load(f)

    # Crear nuevo DataFrame con los datos actualizados
    df_result = pd.DataFrame(datos_actualizados)

    # Segunda validación después de Location Finder
    registros_validos = []
    for _, row in df_result.iterrows():
        if aplicar_filtros("XML", row['nomMonumento'], row['nomProvincia'], row['nomLocalidad'], 
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