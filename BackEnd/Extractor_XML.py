import os

import pandas as pd
import xml.etree.ElementTree as ET
import re
from Location_Finder import LocationFinder
from utils.filtros import get_tipo_monumento, clean_coordinates, clean_html_text

# Change the current working directory
os.chdir('/Users/arnau1146/IdeaProjects/IEIProject/BackEnd')

# Print the current working directory for debugging purposes
print("Current working directory:", os.getcwd())

# Remove '/BackEnd/API' from the file_path if it exists
file_path = xml_path.replace('/BackEnd/API', '')

# Print the full path to the file for debugging purposes
full_path = os.path.join(os.getcwd(), file_path)
print("Full path to the file:", full_path)

tree = ET.parse(xml_path)
root = tree.getroot()

# Leer el archivo XML
xml_path = '../Fuentes_de_datos/Demo/cle.xml'

# Diccionario para almacenar los datos extraídos
data = {
    'nomMonumento': [],
    'tipoMonumento': [],
    'direccion': [],
    'codigo_postal': [],
    'longitud': [],
    'latitud': [],
    'descripcion': [],
    'codLocalidad': [],
    'nomLocalidad': [],
    'codProvincia': [],
    'nomProvincia': []
}

# Extraer información de cada elemento del XML
for monumento in root.findall('.//monumento'):
    nomMonumento = monumento.find('nombre').text if monumento.find('nombre') is not None else pd.NA
    tipoMonumento = monumento.find('tipoMonumento').text if monumento.find('tipoMonumento') is not None else pd.NA
    tipoMonumento = get_tipo_monumento(tipoMonumento)  # Clasificar el tipo de monumento, filtros.py

    # Obtener dirección de la calle
    direccion = monumento.find('calle').text if monumento.find('calle') is not None else pd.NA
    codigo_postal = monumento.find('codigoPostal').text if monumento.find('codigoPostal') is not None else pd.NA
    
    # Obtener coordenadas
    coordenadas = monumento.find('coordenadas')
    if coordenadas is not None:
        longitud = coordenadas.find('longitud').text if coordenadas.find('longitud') is not None else pd.NA
        latitud = coordenadas.find('latitud').text if coordenadas.find('latitud') is not None else pd.NA
        longitud = clean_coordinates(longitud)
        latitud = clean_coordinates(latitud)
    else:
        longitud = pd.NA
        latitud = pd.NA
    
    # Obtener descripción
    descripcion = monumento.find('Descripcion').text if monumento.find('Descripcion') is not None else pd.NA
    descripcion = clean_html_text(descripcion)
    
    # Obtener información de población
    poblacion = monumento.find('poblacion')
    if poblacion is not None:
        nomLocalidad = poblacion.find('localidad').text if poblacion.find('localidad') is not None else pd.NA
        nomProvincia = poblacion.find('provincia').text if poblacion.find('provincia') is not None else pd.NA
    else:
        nomLocalidad = pd.NA
        nomProvincia = pd.NA
    
    codLocalidad = pd.NA  # Generar según necesidad
    codProvincia = pd.NA  # Generar según necesidad

    # Añadir los datos al diccionario
    data['nomMonumento'].append(nomMonumento)
    data['tipoMonumento'].append(tipoMonumento)
    data['direccion'].append(direccion)
    data['codigo_postal'].append(codigo_postal)
    data['latitud'].append(latitud)
    data['longitud'].append(longitud)
    data['descripcion'].append(descripcion)
    data['codLocalidad'].append(codLocalidad)
    data['nomLocalidad'].append(nomLocalidad)
    data['codProvincia'].append(codProvincia)
    data['nomProvincia'].append(nomProvincia)

# Crear un DataFrame con los datos extraídos
df_result = pd.DataFrame(data)

# Eliminar monumentos duplicados por el nombre 'nomMonumento' antes de continuar
df_result_unique = df_result.drop_duplicates(subset='nomMonumento', keep='first')

# Separar los datos en dos DataFrames (con y sin coordenadas)
df_con_coords = df_result_unique.dropna(subset=['longitud', 'latitud'])
df_sin_coords = df_result_unique[df_result_unique['longitud'].isna() | df_result_unique['latitud'].isna()]

# Mostrar información sobre los datos separados
print(f"Monumentos con coordenadas: {len(df_con_coords)}")
print(f"Monumentos sin coordenadas: {len(df_sin_coords)}")

# Guardar los datos en formato JSON sin duplicados
df_con_coords.to_json(
    '../Resultados/XMLtoJSON_con_coords.json',
    orient='records',
    force_ascii=False,
    indent=4,
    default_handler=str
)

if len(df_sin_coords) > 0:
    df_sin_coords.to_json(
        '../Resultados/XMLtoJSON_sin_coords.json',
        orient='records',
        force_ascii=False,
        indent=4,
        default_handler=str
    )

# Procesar el archivo con coordenadas
json_path = '../Resultados/XMLtoJSON_con_coords.json'
location_finder = LocationFinder(json_path)
results = location_finder.process_json()
location_finder.save_results_to_json(results)
print(f"Archivo final guardado en {json_path}.")