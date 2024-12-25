import os
from config.paths import INPUT_JSON_PATH
import pandas as pd
import json
from Location_Finder import LocationFinder
from utils.Filtros import clean_coordinates, limpiar_campo_duplicado, validar_coordenadas, get_tipo_monumento, is_duplicate_monument, procesar_datos
from utils.Otros import *

# Función para cargar el archivo JSON y preservar claves duplicadas
def parse_json_with_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Utilizamos object_pairs_hook para conservar el orden y los duplicados
        data = json.load(file, object_pairs_hook=lambda pairs: pairs)
    return data


# Función para extraer los datos de cada monumento del JSON
def extraer_datos_monumento(monumento, seen_monuments):
    monumento_dict = {key: value for key, value in monumento}
    nomMonumento = monumento_dict.get('documentName', pd.NA)
    address_list = [value for key, value in monumento if key == 'address' and isinstance(value, str)]
    direccion = next((addr for addr in address_list if addr.strip()), pd.NA)
    tipoMonumento = get_tipo_monumento(nomMonumento) if nomMonumento is not pd.NA else pd.NA
    codigo_postal = monumento_dict.get('postalCode', pd.NA)
    latlong = monumento_dict.get('latitudelongitude', '').split(',')

    if len(latlong) == 2:
        latitud = latlong[0]
        longitud = latlong[1]
    else:
        latitud = monumento_dict.get('latwgs84', pd.NA)
        longitud = monumento_dict.get('lonwgs84', pd.NA)

    descripcion = monumento_dict.get('documentDescription', pd.NA)
    codLocalidad = monumento_dict.get('municipalitycode', pd.NA)
    nomLocalidad = monumento_dict.get('municipality', pd.NA)
    codProvincia = monumento_dict.get('territorycode', pd.NA)
    nomProvincia = monumento_dict.get('territory', pd.NA)

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

# Ruta al archivo JSON
json_path = INPUT_JSON_PATH

# Cargar los datos preservando los campos duplicados
json_data = parse_json_with_duplicates(json_path)

# Diccionario para almacenar los datos extraídos
data = { 'nomMonumento': [], 'tipoMonumento': [], 'direccion': [], 'codigo_postal': [], 'longitud': [], 'latitud': [], 'descripcion': [], 'codLocalidad': [], 'nomLocalidad': [], 'codProvincia': [], 'nomProvincia': [] }
seen_monuments = set()

# Extraer los datos
for monumento in json_data:
    extracted_data = extraer_datos_monumento(monumento, seen_monuments)
    if extracted_data:
        for key, value in extracted_data.items():
            data[key].append(value)

# Procesar los datos y extraer la información relevante
df_result = pd.DataFrame(data)

# Dividir los datos en aquellos con coordenadas y sin coordenadas
df_con_coords, df_sin_coords = procesar_datos(data, 'jsontojson')


# Aplica los filtros al DataFrame
df_result = aplicar_correcciones(df_result)

# Guardar el resultado en un archivo JSON
process_and_save_json('Resultados/JSONtoJSON_con_coords.json')
