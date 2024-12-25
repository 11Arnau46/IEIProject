import os
import pandas as pd
import xml.etree.ElementTree as ET
import re
from config.paths import INPUT_XML_PATH
from Location_Finder import LocationFinder
from utils.Filtros import get_tipo_monumento, clean_coordinates, clean_html_text, procesar_datos
from utils.Otros import *

# Función para extraer los datos del XML
def extraer_datos_xml(monumento, seen_monuments):
    nomMonumento = monumento.find('nombre').text if monumento.find('nombre') is not None else pd.NA
    tipoMonumento = get_tipo_monumento(monumento.find('tipoMonumento').text if monumento.find('tipoMonumento') is not None else pd.NA)
    direccion = monumento.find('calle').text if monumento.find('calle') is not None else pd.NA
    codigo_postal = monumento.find('codigoPostal').text if monumento.find('codigoPostal') is not None else pd.NA
    coordenadas = monumento.find('coordenadas')
    longitud = coordenadas.find('longitud').text if coordenadas is not None and coordenadas.find('longitud') is not None else pd.NA
    latitud = coordenadas.find('latitud').text if coordenadas is not None and coordenadas.find('latitud') is not None else pd.NA
    descripcion = clean_html_text(monumento.find('Descripcion').text if monumento.find('Descripcion') is not None else pd.NA)
    poblacion = monumento.find('poblacion')
    nomLocalidad = poblacion.find('localidad').text if poblacion is not None and poblacion.find('localidad') is not None else pd.NA
    nomProvincia = poblacion.find('provincia').text if poblacion is not None and poblacion.find('provincia') is not None else pd.NA
    codLocalidad = pd.NA
    codProvincia = pd.NA

    # Validar utilizando la función de filtros
    if not aplicar_filtros(nomMonumento, nomProvincia, nomLocalidad, seen_monuments):
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
        'codLocalidad': codLocalidad,
        'nomLocalidad': nomLocalidad,
        'codProvincia': codProvincia,
        'nomProvincia': nomProvincia
    }

# Cambiar directorio de trabajo
#os.chdir('/Users/arnau1146/IdeaProjects/IEIProject/BackEnd')
print("Current working directory:", os.getcwd())

# Leer el archivo XML
tree = ET.parse(INPUT_XML_PATH)
root = tree.getroot()

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
seen_monuments = set()

# Extraer información de cada monumento del XML
for monumento in root.findall('.//monumento'):
    extracted_data = extraer_datos_xml(monumento, seen_monuments)
    for key, value in extracted_data.items():
        data[key].append(value)

# Crear DataFrame con los datos extraídos
df_result = pd.DataFrame(data)

# Aplicar filtros estandarizados al DataFrame
df_result = aplicar_correcciones(df_result)

# Dividir los datos en aquellos con coordenadas y sin coordenadas
df_con_coords, df_sin_coords = procesar_datos(data, 'xmltojson')

# Procesar y guardar el archivo JSON
process_and_save_json('../Resultados/XMLtoJSON_con_coords.json')