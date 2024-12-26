import os
import json
from .Filtros import capitalizar_string, clean_coordinates, coordenadas_fuera_de_rango, coordenadas_null, cp_añadir_cero_izquierda, cp_fuera_de_rango, cp_menor_5_digitos, cp_null, direccion_null, limpiar_campo_duplicado, is_duplicate_monument, obtener_despues_del_slash, provincia_incorrecta, provincia_sin_tilde, validar_provincia_localidad
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

    """
    # Validar provincia y localidad
    if not validar_provincia_localidad(nomProvincia, tipo="provincia"):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Provincia inválida}}")
        print(f"Provincia inválida: fuente = {fuente}, monumento = {nomMonumento}, provincia = {nomProvincia}. Rechazado el monumento.")
        return False
    """
    if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
        logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Localidad inválida}}")
        print(f"Localidad inválida: fuente = {fuente}, monumento = {nomMonumento}, localidad = {nomLocalidad}. Rechazado el monumento.")
        return False
    
    # Verificar que la provincia esté bien escrita, primero comprueba si todas las letras son iguales y luego comprueba si hay errores de acentuación. Si hay error de tilde, no se rechaza ya que lo reparamos
    if provincia_sin_tilde(nomProvincia, fuente):
        # Comprobar que esté bien escrita
        if provincia_incorrecta(nomProvincia, fuente):
            logging.error(f"Registros con errores y descartados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomProvincia}, motivo del error = Provincia inválida}}")
            print(f"Provincia inválida: fuente = {fuente}, monumento = {nomMonumento}, localidad = {nomProvincia}. Rechazado el monumento.")
            return False
        
        logging.error(f"Registros con errores y reparado: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomProvincia}, motivo del error = Provincia sin tilde, operación realizada = Reparado mediante la adición de la tilde}}")
        print(f"Provincia inválida: fuente = {fuente}, monumento = {nomMonumento}, localidad = {nomProvincia}. Reparado mediante la adición de la tilde.")
        return True
    
    # Verificar que el codigo postal tenga valor, no rechaza la entrada ya que lo corregimos
    if cp_null(codigoPostal, fuente):
        logging.info(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal sin valor, operación realizada = Reparado mediante la búsqueda del código postal}}")
        print(f"Código postal sin valor: fuente = {fuente}, monumento = {nomMonumento}, codigo postal = {nomLocalidad}. Reparado el monumento mediante la búsqueda del código postal.")
        return True

    # Verificar que el codigo postal tenga 5 dígitos, no rechaza la entrada ya que lo corregimos
    if  cp_menor_5_digitos(codigoPostal, fuente):
        logging.error(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Código postal con menos de 5 digitos, operación realizada = Reparado mediante la adición de 0 a la izquierda}}")
        print(f"Código postal con menos de 5 digitos: fuente = {fuente}, monumento = {nomMonumento}, codigo postal = {codigoPostal}. Reparado mediante la adición de 0 a la izquierda.")
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
    
    # Verificar que la dirección tenga valor, no rechaza la entrada ya que lo corregimos
    if direccion_null(direccion, fuente):
        logging.info(f"Registros con errores y reparados: {{fuente = {fuente}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo del error = Dirección sin valor, operación realizada = Reparado mediante la búsqueda de la dirección}}")
        print(f"Dirección sin valor: fuente = {fuente}, monumento = {nomMonumento}, codigo postal = {nomLocalidad}. Reparado el monumento mediante la búsqueda de la dirección.")
        return True

    return True