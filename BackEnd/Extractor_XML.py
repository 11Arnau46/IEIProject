import os

from config.paths import INPUT_XML_PATH
import pandas as pd
import xml.etree.ElementTree as ET
import re
from Location_Finder import LocationFinder
from utils.filtros import get_tipo_monumento, clean_coordinates, clean_html_text

# Función para extraer los datos del XML
def extraer_datos_xml(monumento):
    nomMonumento = monumento.find('nombre').text if monumento.find('nombre') is not None else pd.NA
    tipoMonumento = get_tipo_monumento(monumento.find('tipoMonumento').text if monumento.find('tipoMonumento') is not None else pd.NA)
    
    direccion = monumento.find('calle').text if monumento.find('calle') is not None else pd.NA
    codigo_postal = monumento.find('codigoPostal').text if monumento.find('codigoPostal') is not None else pd.NA
    
    coordenadas = monumento.find('coordenadas')
    longitud = clean_coordinates(coordenadas.find('longitud').text if coordenadas is not None and coordenadas.find('longitud') is not None else pd.NA)
    latitud = clean_coordinates(coordenadas.find('latitud').text if coordenadas is not None and coordenadas.find('latitud') is not None else pd.NA)

    descripcion = clean_html_text(monumento.find('Descripcion').text if monumento.find('Descripcion') is not None else pd.NA)

    poblacion = monumento.find('poblacion')
    nomLocalidad = poblacion.find('localidad').text if poblacion is not None and poblacion.find('localidad') is not None else pd.NA
    nomProvincia = poblacion.find('provincia').text if poblacion is not None and poblacion.find('provincia') is not None else pd.NA
    
    codLocalidad = pd.NA
    codProvincia = pd.NA

    return {
        'nomMonumento': nomMonumento,
        'tipoMonumento': tipoMonumento,
        'direccion': direccion,
        'codigo_postal': codigo_postal,
        'latitud': latitud,
        'longitud': longitud,
        'descripcion': descripcion,
        'codLocalidad': codLocalidad,
        'nomLocalidad': nomLocalidad,
        'codProvincia': codProvincia,
        'nomProvincia': nomProvincia
    }

# Cambiar directorio de trabajo
os.chdir('/Users/arnau1146/IdeaProjects/IEIProject/BackEnd')
print("Current working directory:", os.getcwd())

# Leer el archivo XML
tree = ET.parse(INPUT_XML_PATH)
root = tree.getroot()

# Diccionario para almacenar los datos extraídos
data = { 'nomMonumento': [], 'tipoMonumento': [], 'direccion': [], 'codigo_postal': [], 'longitud': [], 'latitud': [], 'descripcion': [], 'codLocalidad': [], 'nomLocalidad': [], 'codProvincia': [], 'nomProvincia': [] }

# Extraer información de cada monumento del XML
for monumento in root.findall('.//monumento'):
    extracted_data = extraer_datos_xml(monumento)
    for key, value in extracted_data.items():
        data[key].append(value)

df_result = pd.DataFrame(data)

df_con_coords, df_sin_coords = procesar_datos(df_result)

# Procesar y guardar el archivo JSON
process_and_save_json('../Resultados/XMLtoJSON_con_coords.json')