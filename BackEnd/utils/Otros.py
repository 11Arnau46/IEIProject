import os
import json
from .Filtros import clean_coordinates, coordenadas_fuera_de_rango, coordenadas_null, cp_fuera_de_rango, cp_null, limpiar_campo_duplicado, is_duplicate_monument, validar_provincia_localidad
from .Location_Finder import LocationFinder
import logging

# Configure logging
log_file_path = os.path.join('Resultados', 'log-summary.log')
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[logging.FileHandler(log_file_path, mode='w'), logging.StreamHandler()])

def process_and_save_json(json_path):
    location_finder = LocationFinder(json_path)
    # Procesar el JSON y obtener los resultados
    results = location_finder.process_json()
    # Guardar los resultados en el archivo
    location_finder.save_results_to_json(results)
    print(f"Archivo final guardado en {json_path}.")
    
    # Contar el número de registros cargados correctamente
    num_records = len(results)
    logging.info(f"Número de registros cargados correctamente: {num_records}")

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

def aplicar_filtros(fuente, nomMonumento, nomProvincia, nomLocalidad, codigoPostal, latitud, longitud, seen_monuments):
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
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Monumento duplicado}}")
        print(f"Monumento duplicado: fuente = {fuente}, monumento = {nomMonumento}. Rechazado el monumento.")
        return False

    # Validar provincia y localidad
    if not validar_provincia_localidad(nomProvincia, tipo="provincia"):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Provincia inválida}}")
        print(f"Provincia inválida: fuente = {fuente}, monumento = {nomMonumento}, provincia = {nomProvincia}. Rechazado el monumento.")
        return False
    
    if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Localidad inválida}}")
        print(f"Localidad inválida: fuente = {fuente}, monumento = {nomMonumento}, localidad = {nomLocalidad}. Rechazado el monumento.")
        return False
    
    # Verificar que el codigo postal tenga valor, no rechaza el CP ya que lo corregimos
    if cp_null(codigoPostal, fuente):
        logging.info(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal sin valor, operación realizada = Reparado mediante la búsqueda del código postal}}")
        print(f"Código postal sin valor: fuente = {fuente}, monumento = {nomMonumento}, codigo postal = {nomLocalidad}. Reparado el monumento mediante la búsqueda del código postal.")
        return True

    # Verificar que el codigo postal esté dentro del rango
    if  cp_fuera_de_rango(codigoPostal, fuente):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal fuera de rango}}")
        print(f"Código postal fuera de rango: fuente = {fuente}, monumento = {nomMonumento}, codigo postal = {codigoPostal}. Rechazado el monumento.")
        return False
    
    # Verificar que las coordenadas tengan valor
    if coordenadas_null(latitud, longitud):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Coordenadas sin valor}}")
        print(f"Coordenadas sin valor: fuente = {fuente}, monumento = {nomMonumento}, latitud = {latitud}, longitud = {longitud}. Rechazado el monumento.")
        return False
    
    # Verificar que las coordenadas estén dentro del rango
    if coordenadas_fuera_de_rango(latitud, longitud, fuente):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Coordenadas fuera de rango}}")
        print(f"Coordenadas fuera de rango: fuente = {fuente}, monumento = {nomMonumento}, latitud = {latitud}, longitud = {longitud}. Rechazado el monumento.")
        return False

    return True