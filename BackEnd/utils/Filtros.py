import pandas as pd
import re

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
def filtrar_por_coordenadas(data):
    con_coords = [
        {k: v[i] for k, v in data.items()}
        for i in range(len(data['nomMonumento']))
        if pd.notna(data['longitud'][i]) and pd.notna(data['latitud'][i])
    ]
    sin_coords = [
        {k: v[i] for k, v in data.items()}
        for i in range(len(data['nomMonumento']))
        if pd.isna(data['longitud'][i]) or pd.isna(data['latitud'][i])
    ]
    return con_coords, sin_coords

# Filtrar filas duplicadas
def is_duplicate_monument(nom_monumento, seen_monuments):
    if nom_monumento in seen_monuments:
        return True  # El monumento ya ha sido procesado
    seen_monuments.add(nom_monumento)
    return False

# Función para limpiar coordenadas
def clean_coordinates(value):
    if value is not None and isinstance(value, str):
        # Mantener solo números, puntos y guiones
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

# Función para validar si las coordenadas están dentro de los límites de WGS84
def validar_coordenadas(latitud, longitud):
    try:
        latitud = float(latitud)
        longitud = float(longitud)
        return -90 <= latitud <= 90 and -180 <= longitud <= 180
    except ValueError:
        return False


# Función para limpiar texto HTML
def clean_html_text(text):
    if pd.isna(text):
        return text
    clean_text = re.sub(r'<[^>]+>', '', text)  # Eliminar etiquetas HTML
    clean_text = clean_text.replace('&oacute;', 'ó').replace('&aacute;', 'á').replace('&eacute;', 'é').replace('&iacute;', 'í').replace('&uacute;', 'ú').replace('&ntilde;', 'ñ')  # Reemplazar caracteres especiales
    clean_text = ' '.join(clean_text.split())  # Eliminar espacios extra
    return clean_text
