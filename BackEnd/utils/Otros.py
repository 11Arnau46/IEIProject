import os
import json
from .Filtros import clean_coordinates, coordenadas_fuera_de_rango, coordenadas_null, cp_fuera_de_rango, limpiar_campo_duplicado, is_duplicate_monument, validar_provincia_localidad
from .Location_Finder import LocationFinder

def process_and_save_json(json_path):
    location_finder = LocationFinder(json_path)
    # Procesar el JSON y obtener los resultados
    results = location_finder.process_json()
    # Guardar los resultados en el archivo
    location_finder.save_results_to_json(results)
    print(f"Archivo final guardado en {json_path}.")

def aplicar_correcciones(df):
    """
    Aplica los filtros estandarizados a las columnas específicas de un DataFrame.
    
    Argumentos:
        df (pd.DataFrame): DataFrame al que se le aplicarán los filtros.

    Retorna:
        pd.DataFrame: DataFrame con los filtros aplicados.
    """
    # Diccionario con columnas y sus funciones de filtro
    filtros = {
        'latitud': clean_coordinates,
        'longitud': clean_coordinates,
        'nomLocalidad': limpiar_campo_duplicado,
        'nomProvincia': limpiar_campo_duplicado,
    }

    # Aplicar los filtros
    for columna, filtro in filtros.items():
        if columna in df.columns:  # Verifica si la columna existe en el DataFrame
            df[columna] = df[columna].apply(filtro)
    
    return df

def aplicar_filtros(nomMonumento, nomProvincia, nomLocalidad, codigoPostal, latitud, longitud, seen_monuments):
    """
    Realiza las validaciones para los datos de cada monumento (duplicado, coordenadas, provincia, localidad).
    
    Argumentos:
        nomMonumento (str): Nombre del monumento.
        nomProvincia (str): Nombre de la provincia.
        nomLocalidad (str): Nombre de la localidad.
        seen_monuments (set): Conjunto que mantiene los monumentos ya vistos para evitar duplicados.
    
    Retorna:
        bool: True si pasa todas las validaciones, False si alguna falla.
    """
    # Verificar si el monumento es duplicado
    if is_duplicate_monument(nomMonumento, seen_monuments):
        print(f"Monumento duplicado: {nomMonumento}. Rechazado el monumento.")
        return False

    # Validar provincia y localidad
    if not validar_provincia_localidad(nomProvincia, tipo="provincia"):
        print(f"Provincia inválida: {nomProvincia}. Rechazado el monumento.")
        return False
    if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
        print(f"Localidad inválida: {nomLocalidad}. Rechazado el monumento.")
        return False
    
    if  cp_fuera_de_rango(codigoPostal):
        print(f"Código postal fuera de rango: {codigoPostal}. Rechazado el monumento.")
        return False
    
    if coordenadas_null(latitud, longitud):
        print(f"Coordenadas sin valor: {nomMonumento}, latitud = {latitud}, longitud = {longitud}. Rechazado el monumento.")
        return False
    
    if coordenadas_fuera_de_rango(latitud, longitud):
        print(f"Coordenadas fuera de rango: {nomMonumento}, latitud = {latitud}, longitud = {longitud}. Rechazado el monumento.")
        return False

    return True