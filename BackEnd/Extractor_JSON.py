import os

from config.paths import INPUT_JSON_PATH
import pandas as pd
import json
import re
from Location_Finder import LocationFinder
from utils.filtros import clean_coordinates, limpiar_campo_duplicado, validar_coordenadas, get_tipo_monumento, is_duplicate_monument, procesar_datos

# Función para cargar el archivo JSON y preservar claves duplicadas
def parse_json_with_duplicates(file_path):
    os.chdir('/Users/arnau1146/IdeaProjects/IEIProject/BackEnd')
    print("Current working directory:", os.getcwd())
    
    file_path = file_path.replace('/BackEnd/API', '')
    full_path = os.path.join(os.getcwd(), file_path)
    print("Full path to the file:", full_path)
    
    with open(full_path, 'r', encoding='utf-8') as file:
        data = json.load(file, object_pairs_hook=lambda pairs: pairs)
    return data

# Función para extraer los datos de cada monumento del JSON
def extraer_datos_monumento(monumento):
    monumento_dict = {key: value for key, value in monumento}
    if is_duplicate_monument(nomMonumento, seen_monuments):
        return None

    # Direcciones
    address_list = [value for key, value in monumento if key == 'address' and isinstance(value, str)]
    
    # Datos del monumento
    nomMonumento = monumento_dict.get('documentName', pd.NA)
    tipoMonumento = get_tipo_monumento(nomMonumento) if nomMonumento is not pd.NA else pd.NA
    direccion = next((addr for addr in address_list if addr.strip()), pd.NA)
    codigo_postal = monumento_dict.get('postalCode', pd.NA)
    
    # Coordenadas
    latlong = monumento_dict.get('latitudelongitude', '').split(',')
    if len(latlong) == 2:
        latitud = clean_coordinates(latlong[0])
        longitud = clean_coordinates(latlong[1])
    else:
        latitud = clean_coordinates(monumento_dict.get('latwgs84', pd.NA))
        longitud = clean_coordinates(monumento_dict.get('lonwgs84', pd.NA))
    
    # Validar coordenadas
    if not validar_coordenadas(latitud, longitud):
        return None  # Si las coordenadas no son válidas, omitimos el monumento
    
    descripcion = monumento_dict.get('documentDescription', pd.NA)
    codLocalidad = limpiar_campo_duplicado(monumento_dict.get('municipalitycode', pd.NA))
    nomLocalidad = limpiar_campo_duplicado(monumento_dict.get('municipality', pd.NA))
    codProvincia = limpiar_campo_duplicado(monumento_dict.get('territorycode', pd.NA))
    nomProvincia = limpiar_campo_duplicado(monumento_dict.get('territory', pd.NA))

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

# Ruta al archivo JSON
json_path = INPUT_JSON_PATH

# Cargar los datos preservando los campos duplicados
json_data = parse_json_with_duplicates(json_path)

# Diccionario para almacenar los datos extraídos
data = { 'nomMonumento': [], 'tipoMonumento': [], 'direccion': [], 'codigo_postal': [], 'longitud': [], 'latitud': [], 'descripcion': [], 'codLocalidad': [], 'nomLocalidad': [], 'codProvincia': [], 'nomProvincia': [] }
    seen_monuments = set()

for monumento in json_data:
    extracted_data = extraer_datos_monumento(monumento, seen_monuments)
        for key, value in extracted_data.items():
            data[key].append(value)

# Procesar los datos y extraer la información relevante
df_result = pd.DataFrame(data)

# Dividir los datos en aquellos con y sin coordenadas
df_con_coords, df_sin_coords = procesar_datos(df_result)

# Guardar el resultado en un archivo JSON
process_and_save_json('../Resultados/JSONtoJSON_con_coords.json')