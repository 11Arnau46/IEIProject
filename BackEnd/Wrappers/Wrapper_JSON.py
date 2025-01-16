import sys
import os
import pandas as pd
import json
from pathlib import Path


from BackEnd.config.paths import INPUT_JSON_PATH
from BackEnd.utils.Filtros import *
from BackEnd.utils.Otros import *
from BackEnd.utils.Conversores import convertir_coordenadas_utm
from BackEnd.utils.Location_Finder import LocationFinder
from BackEnd.utils.Coords_converter import CoordsConverter


# Función para cargar el archivo JSON y preservar claves duplicadas
def parse_json_with_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Utilizamos object_pairs_hook para conservar el orden y los duplicados
        data = json.load(file, object_pairs_hook=lambda pairs: pairs)
    return data

def process_json():
    # Configurar la fuente de datos y los loggers
    #if len(sys.argv) > 1:
    #    data_source = sys.argv[1]
    #    set_data_source(data_source)
    #    setup_loggers(data_source)
    
    data_source = "json"
    set_data_source(data_source)
    setup_loggers(data_source)

    # Directorio actual
    print("Current working directory:", os.getcwd())
    
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
        nomLocalidad = monumento_dict.get('municipality', pd.NA)
        nomProvincia = monumento_dict.get('territory', pd.NA)

        # Validar utilizando la función de filtros
        if not aplicar_filtros('JSON', nomMonumento, nomProvincia, nomLocalidad, codigo_postal, latitud, longitud, direccion, seen_monuments):
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

    # Ruta al archivo JSON
    json_path = INPUT_JSON_PATH

    # Cargar los datos preservando los campos duplicados
    json_data = parse_json_with_duplicates(json_path)

    # Contar monumentos
    num_monumentos = len(json_data)

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

    # Extraer los datos
    for monumento in json_data:
        extracted_data = extraer_datos_monumento(monumento, seen_monuments)
        if extracted_data:
            for key, value in extracted_data.items():
                data[key].append(value)

    # Procesar los datos y extraer la información relevante
    df_result = pd.DataFrame(data)

    # Aplica los filtros al DataFrame
    df_result = aplicar_correcciones(df_result)

    # Dividir los datos en aquellos con coordenadas y sin coordenadas y filtrar monumentos repetidos 
    df_con_coords, df_sin_coords = procesar_datos(df_result, 'jsontojson')

    # Get the root project directory
    root_dir = Path(__file__).resolve().parents[2]

    # Define the path to the output JSON file
    ruta_json_salida = root_dir / 'Resultados' / 'JSONtoJSON_con_coords.json'

    # Procesar y guardar el JSON
    process_and_save_json(ruta_json_salida)

    # Cargar los datos actualizados
    with open(ruta_json_salida, 'r', encoding='utf-8') as f:
        datos_actualizados = json.load(f)

    # Crear nuevo DataFrame con los datos actualizados
    df_result = pd.DataFrame(datos_actualizados)

    # Segunda validación después de Location Finder
    registros_validos = []
    for _, row in df_result.iterrows():
        if aplicar_filtros("JSON", row['nomMonumento'], row['nomProvincia'], row['nomLocalidad'], 
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