import os

from config.paths import INPUT_CSV_PATH, OUTPUT_CSV_PATHS
import pandas as pd
import Coords_converter
import json
from Location_Finder import LocationFinder
from utils.filtros import get_tipo_monumento, clean_coordinates, is_duplicate_monument, filtrar_por_coordenadas

# Directorio actual
print("Current working directory:", os.getcwd())

# Leer el archivo CSV
csv_path = '../Fuentes_de_datos/Demo/vcl.csv'
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
    'codLocalidad': [],
    'nomLocalidad': [],
    'codProvincia': [],
    'nomProvincia': []
}

# Conjunto para realizar un seguimiento de los monumentos ya procesados
seen_monuments = set()

# Extraer información de cada fila del CSV
for _, row in df.iterrows():
    nomMonumento = row['DENOMINACION']
    
    # Verificar si el monumento ya ha sido procesado, filtros.py
    if is_duplicate_monument(nomMonumento, seen_monuments):
        continue  
    
    # Obtener el tipo de monumento, filtros.py
    tipoMonumento = get_tipo_monumento(nomMonumento)

    # Extraer los demás datos
    direccion = pd.NA 
    codigo_postal = pd.NA
    latitud = row['UTMNORTE'] if pd.notnull(row['UTMNORTE']) else pd.NA 
    longitud = row['UTMESTE'] if pd.notnull(row['UTMESTE']) else pd.NA
    descripcion = row['CLASIFICACION']
    codLocalidad = pd.NA 
    nomLocalidad = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else pd.NA
    codProvincia = pd.NA 
    nomProvincia = row['PROVINCIA'] if pd.notnull(row['PROVINCIA']) else pd.NA

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

    # Agregar el nombre del monumento al conjunto de monumentos procesados
    seen_monuments.add(nomMonumento)

# Separar los datos en dos DataFrames, filtros.py
con_coords, sin_coords = filtrar_por_coordenadas(data)

# Guardar los datos en formato JSON con formato legible
con_coords.to_json(
    'Resultados/CSVtoJSON_con_coords.json',
    orient='records',
    force_ascii=False,
    indent=4,
    default_handler=str
)
if len(df_sin_coords) > 0:
    sin_coords.to_json(
        'Resultados/CSVtoJSON_sin_coords.json',
        orient='records',
        force_ascii=False,
        indent=4,
        default_handler=str
    )

#Hacer conversión de coordenadas a grados con Selenium
#https://www.ign.es/web/calculadora-geodesica

ruta_json_entrada = "Resultados/CSVtoJSON_con_coords.json"  # Cambia por tu archivo JSON
ruta_json_salida = "Resultados/CSVtoJSON_Corregido.json"

with open(ruta_json_entrada, "r", encoding="utf-8") as file:
    monumentos = json.load(file)

# Actualiza los datos del JSON
for monumento in monumentos:
    if monumento["latitud"] and monumento["longitud"]:
        print(f"Convirtiendo coordenadas UTM para {monumento['nomMonumento']}...")
        lat, lon = Coords_converter.convert_utm(monumento["latitud"], monumento["longitud"])
        if lat and lon:
            monumento["latitud"] = lat
            monumento["longitud"] = lon

# Guarda el archivo actualizado
with open(ruta_json_salida, "w", encoding="utf-8") as file:
    json.dump(monumentos, file, ensure_ascii=False, indent=4)

print(f"Archivo actualizado guardado en {ruta_json_salida}.")


# todo: Poner el archivo con coordenadas
#Usar la API para obtener el Código Postal y Localidad
json_path = 'Resultados/CSVtoJSON_Corregido.json'
location_finder = LocationFinder(json_path)
# Procesar el JSON y guardar los resultados en el mismo archivo con código postal y direcciones completas
results = location_finder.process_json()
location_finder.save_results_to_json(results)