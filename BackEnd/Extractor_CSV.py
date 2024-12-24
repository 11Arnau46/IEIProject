import os

from config.paths import INPUT_CSV_PATH
import pandas as pd
import Coords_converter
import json
from Location_Finder import LocationFinder
from utils.filtros import get_tipo_monumento, clean_coordinates, is_duplicate_monument, filtrar_por_coordenadas

# Directorio actual
print("Current working directory:", os.getcwd())

# Función para extraer los datos del CSV
def extraer_datos_csv(row, seen_monuments):
    nomMonumento = row['DENOMINACION']
    if is_duplicate_monument(nomMonumento, seen_monuments):
        return None

    tipoMonumento = get_tipo_monumento(nomMonumento)
    direccion = pd.NA
    codigo_postal = pd.NA
    latitud = row['UTMNORTE'] if pd.notnull(row['UTMNORTE']) else pd.NA
    longitud = row['UTMESTE'] if pd.notnull(row['UTMESTE']) else pd.NA
    descripcion = row['CLASIFICACION']
    codLocalidad = pd.NA
    nomLocalidad = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else pd.NA
    codProvincia = pd.NA
    nomProvincia = row['PROVINCIA'] if pd.notnull(row['PROVINCIA']) else pd.NA

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

# Leer el archivo CSV
csv_path = INPUT_CSV_PATH
df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')

# Diccionario para almacenar los datos extraídos
data = { 'nomMonumento': [], 'tipoMonumento': [], 'direccion': [], 'codigo_postal': [], 'longitud': [], 'latitud': [], 'descripcion': [], 'codLocalidad': [], 'nomLocalidad': [], 'codProvincia': [], 'nomProvincia': [] }
seen_monuments = set()

# Extraer información de cada fila del CSV
for _, row in df.iterrows():
    extracted_data = extraer_datos_csv(row, seen_monuments)
    if extracted_data:
        for key, value in extracted_data.items():
            data[key].append(value)

df_result = pd.DataFrame(data)

df_con_coords, df_sin_coords = procesar_datos(df_result)

# Rutas de archivos
ruta_json_entrada = "../Resultados/CSVtoJSON_con_coords.json"
ruta_json_salida = "../Resultados/CSVtoJSON_Corregido.json"

# Convertir coordenadas y procesar el archivo
convertir_coordenadas_utm(ruta_json_entrada, ruta_json_salida)
process_and_save_json('../Resultados/CSVtoJSON_Corregido.json')