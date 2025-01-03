import sys
import os
import pandas as pd
import Coords_converter
import json
from pathlib import Path
from config.paths import INPUT_CSV_PATH
from utils.Filtros import *
from utils.Otros import *
from utils.Conversores import convertir_coordenadas_utm
from utils.Location_Finder import LocationFinder

# Configurar la fuente de datos y los loggers
if len(sys.argv) > 1:
    data_source = sys.argv[1]
    set_data_source(data_source)
    setup_loggers(data_source)

# Directorio actual
print("Current working directory:", os.getcwd())

# Función para extraer los datos del CSV
def extraer_datos_csv(row, seen_monuments):
    nomMonumento = row['DENOMINACION']
    tipoMonumento = get_tipo_monumento(nomMonumento)
    direccion = pd.NA
    codigo_postal = pd.NA
    latitud = row['UTMNORTE'] if pd.notnull(row['UTMNORTE']) else pd.NA
    longitud = row['UTMESTE'] if pd.notnull(row['UTMESTE']) else pd.NA
    descripcion = row['CLASIFICACION']
    nomLocalidad = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else pd.NA
    nomProvincia = row['PROVINCIA'] if pd.notnull(row['PROVINCIA']) else pd.NA

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

# Leer el archivo CSV
csv_path = INPUT_CSV_PATH
df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')

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

# Extraer información de cada fila del CSV
for _, row in df.iterrows():
    extracted_data = extraer_datos_csv(row, seen_monuments)
    if extracted_data is not None:  # Solo agregar si los datos no son None
        for key, value in extracted_data.items():
            data[key].append(value)

# Crear DataFrame con los datos extraídos
df_result = pd.DataFrame(data)

# Mostrar información sobre los datos separados

# Aplicar filtros estandarizados al DataFrame
df_result = aplicar_correcciones(df_result)

# Dividir los datos en aquellos con coordenadas y sin coordenadas y filtrar monumentos repetidos 
df_con_coords, df_sin_coords = procesar_datos(df_result, 'csvtojson')

# Get the root project directory
root_dir = Path(__file__).resolve().parents[1]

# Convertir coordenadas
ruta_json_entrada = root_dir / 'Resultados' / 'CSVtoJSON_con_coords.json'
ruta_json_salida = root_dir / 'Resultados' / 'CSVtoJSON_Corregido.json'

# Print the paths for debugging purposes
print(f"Path to input JSON: {ruta_json_entrada}")
print(f"Path to output JSON: {ruta_json_salida}")

# Check if the input file exists
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