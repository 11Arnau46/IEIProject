import os
import json
from .Filtros import capitalizar_string, clean_coordinates, coordenadas_fuera_de_rango, coordenadas_null, cp_añadir_cero_izquierda, cp_fuera_de_rango, cp_de_4_digitos, cp_null, direccion_null, limpiar_campo_duplicado, is_duplicate_monument, obtener_despues_del_slash, provincia_incorrecta, provincia_sin_tilde, validar_provincia_localidad
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
    
    # Contar el número de registro cargados correctamente
    num_records = len(results)
    total_records_added_correctly += num_records
    
    logging.info("")
    logging.info(f"Número de registro cargados correctamente : {num_records}")
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
    
    # Tratar el código postal de manera especial para poder pasar el nombre y localidad
    if 'codigo_postal' in df.columns:
        df['codigo_postal'] = df.apply(lambda row: cp_añadir_cero_izquierda(row['codigo_postal'], row['nomMonumento'], row['nomLocalidad']), axis=1)
    
    return df

def aplicar_filtros(fuente, nomMonumento, nomProvincia, nomLocalidad, codigoPostal, latitud, longitud, direccion, seen_monuments, pasadoPorLocationFinder = False):
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
        logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Monumento duplicado}}")
        return False

    # Verificar que las coordenadas tengan valor
    if coordenadas_null(latitud, longitud):
        logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Coordenadas sin valor}}")
        return False

    # Verificar que las coordenadas estén dentro del rango
    if fuente == "XML" or fuente == "JSON":
        if coordenadas_fuera_de_rango(latitud, longitud, fuente):
            logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Coordenadas fuera de rango}}")
            return False
    
    if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
        logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Localidad inválida}}")
        return False

    # Verificar que la provincia esté bien escrita.
    if provincia_incorrecta(nomProvincia, fuente):
        logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomProvincia}, motivo del error = Provincia inválida}}")
        return False
    
    
    # Verificar que la provincia tiene las tildes correctas.
    # Se deja continuar si no tiene tilde ya que se puede reparar en la siguiente etapa.
    if provincia_sin_tilde(nomProvincia, fuente):
        logging.info(f"Registro rechazado: {{nombre = {nomMonumento}, Localidad = {nomProvincia}, motivo del error = Provincia sin tilde, operación realizada = Intentar reparar en la siguiente etapa}}")
        return True
    
    # Verificar que el codigo postal tenga valor y no sea 'N/A'.
    # Se deja continuar si no tiene valor ya que se puede reparar en la siguiente etapa.
    if cp_null(codigoPostal, fuente) or str(codigoPostal).upper() == 'N/A':
        if pasadoPorLocationFinder:
            logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal sin valor o N/A}}, no se ha podido reparar")
            return False
        else:
            logging.info(f"Registro rechazado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal sin valor o N/A, operación realizada = Intentar reparar en la siguiente etapa}}")
            return True
    
    # Verificar que el codigo postal tenga 4 dígitos. 
    # Si tiene 4 dígitos, se añade un 0 a la izquierda.
    
    if cp_de_4_digitos(codigoPostal, fuente, nomMonumento, nomLocalidad) == -1:
        logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal con menos de 4 digitos}}")
        return False
    
    if cp_de_4_digitos(codigoPostal, fuente, nomMonumento, nomLocalidad) == 1:
        logging.info(f"Registro rechazado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal con menos de 5 digitos, operación realizada = Reparado mediante la adición de 0 a la izquierda}}")
        return True
    
    # Verificar que el codigo postal esté dentro del rango
    if cp_fuera_de_rango(codigoPostal, fuente):
        logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal fuera de rango}}")
        return False
    
    # Verificar que la dirección tenga valor. No se rechaza el monumento ya que luego se repara
    if direccion_null(direccion, fuente, pasadoPorLocationFinder):
        if pasadoPorLocationFinder:
            logging.error(f"Registro descartado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Dirección sin valor}}")
            return False
        else:
            logging.info(f"Registro rechazado: {{nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Dirección sin valor, operación realizada = Intentar reparar en la siguiente etapa}}")
            return True
    return True


def get_total_records_added_correctly():
    """
    Devuelve el número total de registro cargados correctamente.
    """
    return total_records_added_correctly