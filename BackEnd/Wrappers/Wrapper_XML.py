import sys
import os
import pandas as pd
import xml.etree.ElementTree as ET
import re
from pathlib import Path
import logging
import json


from BackEnd.config.paths import INPUT_XML_PATH
from BackEnd.utils.Location_Finder import LocationFinder
from BackEnd.utils.Filtros import get_tipo_monumento, clean_coordinates, clean_html_text, procesar_datos
from BackEnd.utils.Otros import *

def process_xml():
    # Configurar la fuente de datos y los loggers
    if len(sys.argv) > 1:
        data_source = sys.argv[1]
        set_data_source(data_source)
        setup_loggers(data_source)

    # Leer el archivo XML
    tree = ET.parse(INPUT_XML_PATH)
    root = tree.getroot()

    # Contar monumentos
    monumentos = root.findall('.//monumento')
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

    # Función para extraer los datos del XML
    def extraer_datos_xml(monumento, seen_monuments):
        nomMonumento = monumento.find('nombre').text if monumento.find('nombre') is not None else pd.NA
        tipoMonumento = get_tipo_monumento(monumento.find('tipoMonumento').text if monumento.find('tipoMonumento') is not None else pd.NA)
        direccion = monumento.find('calle').text if monumento.find('calle') is not None else pd.NA
        codigo_postal = str(monumento.find('codigoPostal').text) if monumento.find('codigoPostal') is not None else pd.NA
        coordenadas = monumento.find('coordenadas')
        longitud = coordenadas.find('longitud').text if coordenadas is not None and coordenadas.find('longitud') is not None else pd.NA
        latitud = coordenadas.find('latitud').text if coordenadas is not None and coordenadas.find('latitud') is not None else pd.NA
        descripcion = clean_html_text(monumento.find('Descripcion').text if monumento.find('Descripcion') is not None else pd.NA)
        poblacion = monumento.find('poblacion')
        nomLocalidad = poblacion.find('localidad').text if poblacion is not None and poblacion.find('localidad') is not None else pd.NA
        nomProvincia = poblacion.find('provincia').text if poblacion is not None and poblacion.find('provincia') is not None else pd.NA

        # Validar utilizando la función de filtros
        if not aplicar_filtros("XML", nomMonumento, nomProvincia, nomLocalidad, codigo_postal, latitud, longitud, direccion, seen_monuments):
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

    # Cambiar directorio de trabajo
    #os.chdir('/Users/arnau1146/IdeaProjects/IEIProject/BackEnd')
    print("Current working directory:", os.getcwd())

    # Extraer información de cada monumento del XML
    for monumento in monumentos:
        extracted_data = extraer_datos_xml(monumento, seen_monuments)    # Verificar si los datos extraídos no son None antes de continuar
        if extracted_data is not None:
            for key, value in extracted_data.items():
                data[key].append(value)

    # Crear DataFrame con los datos extraídos
    df_result = pd.DataFrame(data)

    # Aplicar filtros estandarizados al DataFrame
    df_result = aplicar_correcciones(df_result)

    # Dividir los datos en aquellos con coordenadas y sin coordenadas y filtrar monumentos repetidos 
    df_con_coords, df_sin_coords = procesar_datos(df_result, 'xmltojson')

    # Get the root project directory
    root_dir = Path(__file__).resolve().parents[2]

    # Define the path to the output JSON file
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
    process_xml()
    