import os
import json
from .Filtros import capitalizar_string, clean_coordinates, coordenadas_fuera_de_rango, coordenadas_null, cp_añadir_cero_izquierda, cp_fuera_de_rango, cp_menor_5_digitos, cp_null, direccion_null, limpiar_campo_duplicado, is_duplicate_monument, obtener_despues_del_slash, provincia_incorrecta, provincia_sin_tilde, validar_provincia_localidad
from .Location_Finder import LocationFinder
from pathlib import Path
import logging


# Get the root project directory
root_dir = Path(__file__).resolve().parents[2]

# Define the relative path to the log file
log_file_path = root_dir / 'Resultados' / 'log-summary.log'

print(f"Log file path: {log_file_path}")

# Configurar el logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    filename=str(log_file_path),
    filemode='w'  # 'w' para sobrescribir el archivo en cada ejecución
)

# Global variable to keep track of the total count of records added correctly
total_records_added_correctly = 0

def process_and_save_json(json_path):
    global total_records_added_correctly
    location_finder = LocationFinder(json_path)
    # Procesar el JSON y obtener los resultados
    results = location_finder.process_json()
    # Guardar los resultados en el archivo
    location_finder.save_results_to_json(results)
    print(f"Archivo final guardado en {json_path}.")
    
    # Contar el número de registros cargados correctamente
    num_records = len(results)
    total_records_added_correctly += num_records
    
    logging.info("")
    logging.info(f"Número de registros cargados correctamente : {num_records}")
    logging.info("--------------------------------------------------------------------------------")

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
        'codigo_postal': cp_añadir_cero_izquierda,
        'nomLocalidad': [limpiar_campo_duplicado, obtener_despues_del_slash, capitalizar_string],
        'nomProvincia': [limpiar_campo_duplicado, obtener_despues_del_slash, capitalizar_string],
    }

    # Aplicar los filtros
    for columna, filtros_a_aplicar in filtros.items():
        if columna in df.columns:  # Verifica si la columna existe en el DataFrame
            # Asegurarse de que filtros_a_aplicar sea siempre iterable
            if not isinstance(filtros_a_aplicar, list):
                filtros_a_aplicar = [filtros_a_aplicar]
            
            for filtro in filtros_a_aplicar:
                df[columna] = df[columna].apply(filtro)
    
    return df

def aplicar_filtros(fuente, nomMonumento, nomProvincia, nomLocalidad, codigoPostal, latitud, longitud, direccion, seen_monuments):
    """
    Realiza las validaciones para los datos de cada monumento (duplicado, coordenadas, provincia, localidad).
    
    Argumentos:
        fuente (str): Origen de los datos (XML, JSON, CSV)
        nomMonumento (str): Nombre del monumento.
        nomProvincia (str): Nombre de la provincia.
        nomLocalidad (str): Nombre de la localidad.
        codigoPostal (str): Código postal.
        latitud (float): Latitud del monumento.
        longitud (float): Longitud del monumento.
        direccion (str): Dirección del monumento.
        seen_monuments (set): Conjunto que mantiene los monumentos ya vistos para evitar duplicados.
    
    Retorna:
        bool: True si pasa todas las validaciones, False si alguna falla.
    """
    # Verificar si el monumento es duplicado
    if is_duplicate_monument(nomMonumento, seen_monuments):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Monumento duplicado}}")
        return False

    # Verificar que las coordenadas tengan valor
    if coordenadas_null(latitud, longitud):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Coordenadas sin valor}}")
        return False

    # Verificar que las coordenadas estén dentro del rango
    if coordenadas_fuera_de_rango(latitud, longitud, fuente):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Coordenadas fuera de rango}}")
        return False

    if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Localidad inválida}}")
        return False
    
    # Verificar que la provincia esté bien escrita
    if provincia_sin_tilde(nomProvincia, fuente):
        # Comprobar que esté bien escrita
        if provincia_incorrecta(nomProvincia, fuente):
            logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomProvincia}, motivo del error = Provincia inválida}}")
            return False
        
        logging.error(f"Registros con errores y reparado: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomProvincia}, motivo del error = Provincia sin tilde, operación realizada = Reparado mediante la adición de la tilde}}")
        return True
    
    # Verificar que el codigo postal tenga valor y no sea 'N/A'
    if cp_null(codigoPostal, fuente) or str(codigoPostal).upper() == 'N/A':
        logging.info(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal sin valor o N/A, operación realizada = Reparado mediante la búsqueda del código postal}}")
        return True  # Permitimos que continúe para que LocationFinder pueda repararlo

    # Verificar que el codigo postal tenga 5 dígitos
    if cp_menor_5_digitos(codigoPostal, fuente):
        logging.error(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal con menos de 5 digitos, operación realizada = Reparado mediante la adición de 0 a la izquierda}}")
        return True
    
    # Verificar que el codigo postal esté dentro del rango
    if cp_fuera_de_rango(codigoPostal, fuente):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal fuera de rango}}")
        return False
    
    # Verificar que la dirección tenga valor
    if direccion_null(direccion, fuente):
        logging.info(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Dirección sin valor, operación realizada = Reparado mediante la búsqueda de la dirección}}")
        return True

    return True


def get_total_records_added_correctly():
    """
    Devuelve el número total de registros cargados correctamente.
    """
    return total_records_added_correctly