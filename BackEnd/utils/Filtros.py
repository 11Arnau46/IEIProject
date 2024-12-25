import pandas as pd
import re
import os
import pycountry
import json

#Filtros que por su naturaleza deben ser colocados uno por uno------------------------------------------------------------------------------

# Función para clasificar el tipo de monumento basado en la denominación
def get_tipo_monumento(denominacion):
    if not isinstance(denominacion, str):
        return pd.NA

    # Normalizamos la denominación a minúsculas para evitar casos duplicados
    denominacion_lower = denominacion.lower()

    # Diccionario con palabras clave para cada tipo
    palabras_clave = {
        "YacimientoArqueologico": ["yacimiento arqueológico", "yacimiento"],
        "MonasterioConvento": ["monasterio", "convento"],
        "IglesiaErmita": ["iglesia", "ermita", "catedral", "basílica"],
        "CastilloFortalezaTorre": ["castillo", "fortaleza", "torre", "fuerte"],
        "EdificioPalacio": ["edificio", "palacio", "jardín", "casas nobles", "paraje", "plazas"],
        "Puente": ["puente"],
    }

    # Iterar por tipo y palabras clave
    for tipo, keywords in palabras_clave.items():
        if any(keyword in denominacion_lower for keyword in keywords):
            return tipo

    # Si no coincide con ningún tipo, retornar "Otros"
    return "Otros"


# Filtrar filas con o sin coordenadas
def procesar_datos(data, archivo_json):
    # Verificar si 'data' es un diccionario y convertirlo a DataFrame
    if isinstance(data, dict):
        data = pd.DataFrame(data)
    
    # Eliminar monumentos duplicados por el nombre 'nomMonumento' antes de continuar
    df_result_unique = data.drop_duplicates(subset='nomMonumento', keep='first')
    
    # Separar los datos en dos DataFrames (con y sin coordenadas)
    df_con_coords = df_result_unique.dropna(subset=['longitud', 'latitud'])
    df_sin_coords = df_result_unique[df_result_unique['longitud'].isna() | df_result_unique['latitud'].isna()]

    # Crear la ruta absoluta correcta para 'Resultados' en el directorio raíz del proyecto
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'IEIProject'))  # Subir tres niveles al directorio raíz
    result_dir = os.path.join(project_root, 'Resultados')
    os.makedirs(result_dir, exist_ok=True)
    
    # Establecer el nombre de archivo basado en el argumento 'archivo_json'
    if archivo_json == 'csvotojson':
        con_coords_path = os.path.join(result_dir, 'CSVtoJSON_con_coords.json')
        sin_coords_path = os.path.join(result_dir, 'CSVtoJSON_sin_coords.json')
    elif archivo_json == 'jsontojson':
        con_coords_path = os.path.join(result_dir, 'JSONtoJSON_con_coords.json')
        sin_coords_path = os.path.join(result_dir, 'JSONtoJSON_sin_coords.json')
    elif archivo_json == 'xmltojson':
        con_coords_path = os.path.join(result_dir, 'XMLtoJSON_con_coords.json')
        sin_coords_path = os.path.join(result_dir, 'XMLtoJSON_sin_coords.json')
    else:
        raise ValueError("El argumento 'archivo_json' debe ser 'csvotojson', 'jsontojson' o 'xmltojson'")

    # Mostrar información sobre los datos separados
    print(f"Monumentos con coordenadas: {len(df_con_coords)}")
    print(f"Monumentos sin coordenadas: {len(df_sin_coords)}")
    
    # Guardar los datos en formato JSON
    print(f"Guardando archivo con coordenadas en: {con_coords_path}")
    df_con_coords.to_json(
        con_coords_path,
        orient='records',
        force_ascii=False,
        indent=4,
        default_handler=str
    )

    if len(df_sin_coords) > 0:
        print(f"Guardando archivo sin coordenadas en: {sin_coords_path}")
        df_sin_coords.to_json(
            sin_coords_path,
            orient='records',
            force_ascii=False,
            indent=4,
            default_handler=str
        )

    return df_con_coords, df_sin_coords

# Filtrar filas duplicadas, caso contrario no continuar
def is_duplicate_monument(nom_monumento, seen_monuments):
    if nom_monumento in seen_monuments:
        return True  # El monumento ya ha sido procesado
    seen_monuments.add(nom_monumento)
    return False
# Función para validar si las coordenadas están dentro de los límites de WGS84, caso contrario no continuar
def validar_coordenadas(latitud, longitud):
        # Comprobar si latitud o longitud son NaN
    if pd.isna(latitud) or pd.isna(longitud):
        return True;
    try:
        latitud = float(latitud)
        longitud = float(longitud)
        # Verificar que la latitud esté entre -90 y 90 y que la longitud esté entre -180 y 180
        if -90 <= latitud <= 90 and -180 <= longitud <= 180:
            return True
        else:
            return False
    except ValueError:
        return False  # Si no se puede convertir a float, la coordenada es inválida

def validar_provincia_localidad(nombre, tipo="provincia"):
    """
    Valida si un nombre corresponde a una provincia o localidad válida en España.

    Argumentos:
        nombre (str): Nombre de la provincia o localidad a validar.
        tipo (str): Tipo de validación ('provincia' o 'localidad').

    Retorna:
        bool: True si es válida, False en caso contrario.
    """
    if pd.isna(nombre):
        return False

    nombre = nombre.strip().lower()  # Normalizar el nombre
    
    if tipo == "provincia":
        provincias = [
            subdivision.name.lower() for subdivision in pycountry.subdivisions if subdivision.country_code == "ES"
        ]
        # Comprobar si el nombre contiene alguna provincia (no exacto, pero contiene la palabra)
        return any(provincia in nombre for provincia in provincias)
    
    elif tipo == "localidad":
        # Esto puede ampliarse con datos específicos de localidades de España
        return True  # Por defecto, se acepta cualquier localidad
    return False 


#Correcciones aplicables en grupo------------------------------------------------------------------------------

# Función para limpiar coordenadas
def clean_coordinates(value):
    if value is not None and isinstance(value, str):
        return re.sub(r'[^0-9\.\-]', '', value)
    return value  

#Elimina palabras duplicadas en el texto
def limpiar_campo_duplicado(valor):
    if not isinstance(valor, str):
        return valor
    # Divide el string por espacios y elimina duplicados manteniendo el orden
    partes = valor.split()
    partes_unicas = []
    for parte in partes:
        if parte not in partes_unicas:
            partes_unicas.append(parte)
    return ' '.join(partes_unicas)

#Excepciones------------------------------------------------------------------------------

# Función para limpiar texto HTML
def clean_html_text(text):
    if pd.isna(text):
        return text
    clean_text = re.sub(r'<[^>]+>', '', text)  # Eliminar etiquetas HTML
    clean_text = clean_text.replace('&oacute;', 'ó').replace('&aacute;', 'á').replace('&eacute;', 'é').replace('&iacute;', 'í').replace('&uacute;', 'ú').replace('&ntilde;', 'ñ')  # Reemplazar caracteres especiales
    clean_text = ' '.join(clean_text.split())  # Eliminar espacios extra
    return clean_text
