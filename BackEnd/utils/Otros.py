import os
import json
from .Filtros import capitalizar_string, clean_coordinates, coordenadas_fuera_de_rango, coordenadas_null, cp_añadir_cero_izquierda, cp_fuera_de_rango, cp_de_4_digitos, cp_null, direccion_null, limpiar_campo_duplicado, is_duplicate_monument, obtener_despues_del_slash, provincia_incorrecta, provincia_sin_tilde, validar_provincia_localidad
from .Location_Finder import LocationFinder
from pathlib import Path
import logging
import sys


# Get the root project directory
root_dir = Path(__file__).resolve().parents[2]

# Variable global para la fuente de datos
data_source = None

def set_data_source(source):
    """
    Establece la fuente de datos global.
    """
    global data_source
    data_source = source.upper()

def get_data_source():
    """
    Obtiene la fuente de datos global.
    """
    return data_source

def setup_loggers(source):
    """
    Configura los loggers según la fuente de datos.
    """
    set_data_source(source)  # Usar la función para establecer la fuente
    
    # Verificar si los loggers ya están configurados
    logger_name = f'reparados_{source.upper()}'
    if logger_name in logging.root.manager.loggerDict:
        # Si ya están configurados, eliminar los handlers existentes
        logger_rechazados = logging.getLogger(f'rechazados_{source.upper()}')
        logger_reparados = logging.getLogger(logger_name)
        logger_estadisticas = logging.getLogger(f'estadisticas_{source.upper()}')
        
        logger_rechazados.handlers.clear()
        logger_reparados.handlers.clear()
        logger_estadisticas.handlers.clear()
    
    # Define las rutas para los diferentes logs
    log_dir = root_dir / 'Resultados' / f'log-{data_source.lower()}'
    os.makedirs(log_dir, exist_ok=True)  # Crear el directorio si no existe

    log_rechazados_path = log_dir / f'log-rechazados-{data_source.lower()}.log'
    log_reparados_path = log_dir / f'log-reparados-{data_source.lower()}.log'
    log_estadisticas_path = log_dir / f'log-estadisticas-{data_source.lower()}.log'

    # Limpiar archivos de log al inicio
    with open(str(log_rechazados_path), 'w') as f:
        f.write("")
    with open(str(log_reparados_path), 'w') as f:
        f.write("")
    with open(str(log_estadisticas_path), 'w') as f:
        f.write("")

    # Configurar el logger para registros rechazados
    logger_rechazados = logging.getLogger(f'rechazados_{data_source}')
    logger_rechazados.setLevel(logging.ERROR)
    logger_rechazados.propagate = False  # Evitar propagación a la salida estándar
    handler_rechazados = logging.FileHandler(str(log_rechazados_path), mode='a')
    handler_rechazados.setFormatter(logging.Formatter('%(message)s'))
    logger_rechazados.addHandler(handler_rechazados)

    # Configurar el logger para registros reparados
    logger_reparados = logging.getLogger(f'reparados_{data_source}')
    logger_reparados.setLevel(logging.INFO)
    logger_reparados.propagate = False  # Evitar propagación a la salida estándar
    handler_reparados = logging.FileHandler(str(log_reparados_path), mode='a')
    handler_reparados.setFormatter(logging.Formatter('%(message)s'))
    logger_reparados.addHandler(handler_reparados)

    # Configurar el logger para estadísticas generales
    logger_estadisticas = logging.getLogger(f'estadisticas_{data_source}')
    logger_estadisticas.setLevel(logging.INFO)
    logger_estadisticas.propagate = False  # Evitar propagación a la salida estándar
    handler_estadisticas = logging.FileHandler(str(log_estadisticas_path), mode='a')
    handler_estadisticas.setFormatter(logging.Formatter('%(message)s'))
    logger_estadisticas.addHandler(handler_estadisticas)
    
    return logger_rechazados, logger_reparados, logger_estadisticas

# Variables globales para contadores
total_records_added_correctly = 0
total_records_rejected = 0
total_records_repaired = 0

def process_and_save_json(json_path):
    global total_records_added_correctly
    location_finder = LocationFinder(json_path)
    # Procesar el JSON y obtener los resultados
    results = location_finder.process_json()
    # Guardar los resultados en el archivo
    location_finder.save_results_to_json(results)
    
    # Contar el número de registro cargados correctamente
    num_records = len(results)
    total_records_added_correctly += num_records

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
        df['codigo_postal'] = df.apply(lambda row: cp_añadir_cero_izquierda(row['codigo_postal']), axis=1)
    
    return df

def borrar_linea_log(fuente, nomMonumento, nomLocalidad, mensaje_a_borrar):
    """Borra una línea específica del log de reparados"""
    log_reparados_path = root_dir / 'Resultados' / f'log-{fuente.lower()}' / f'log-reparados-{fuente.lower()}.log'
    with open(log_reparados_path, 'r') as file:
        lines = file.readlines()
    with open(log_reparados_path, 'w') as file:
        for line in lines:
            if not f"nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo = {mensaje_a_borrar}" in line:
                file.write(line)

def get_community_name(source):
    """
    Obtiene el nombre de la comunidad según la fuente de datos.
    """
    source_names = {
        'XML': 'Castilla y León',
        'CSV': 'Comunidad Valenciana',
        'JSON': 'Euskadi'
    }
    return source_names.get(source, source)

def log_error(logger, fuente, nomMonumento, nomLocalidad, motivo):
    """
    Función auxiliar para generar logs de error con el nombre correcto de la comunidad.
    """
    community_name = get_community_name(fuente)
    logger.error(f"{{fuente = {community_name}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo = {motivo}}}")

def log_repair(logger, fuente, nomMonumento, nomLocalidad, motivo, operacion):
    """
    Función auxiliar para generar logs de reparación con el nombre correcto de la comunidad.
    """
    community_name = get_community_name(fuente)
    logger.info(f"{{fuente = {community_name}, nombre = {nomMonumento}, Localidad = {nomLocalidad}, motivo = {motivo}, operación = {operacion}}}")

def aplicar_filtros(fuente, nomMonumento, nomProvincia, nomLocalidad, codigoPostal, latitud, longitud, direccion, seen_monuments, pasadoPorLocationFinder = False):
    """
    Realiza las validaciones para los datos de cada monumento (duplicado, coordenadas, provincia, localidad).
    """
    global total_records_rejected, total_records_repaired, total_records_added_correctly
    
    # Obtener los loggers específicos para la fuente
    logger_rechazados = logging.getLogger(f'rechazados_{fuente}')
    logger_reparados = logging.getLogger(f'reparados_{fuente}')
    
    # Primera validación: verificar si el monumento ya existe en la base de datos
    try:
        from SQL.BDConnection import BDConnection
        bd_connection = BDConnection()
        bd_connection.init_db("carga")
        existing_monuments = bd_connection.get_existing_monuments()
        bd_connection.close()

        # Comparar con los monumentos existentes
        for monument in existing_monuments:
            if monument.nombre.lower() == nomMonumento.lower():
                log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Monumento ya existe en la base de datos")
                total_records_rejected += 1
                return False
    except Exception as e:
        print(f"Error al verificar duplicados en la base de datos: {str(e)}")

    # Segunda validación: verificar si el monumento está duplicado en la carga actual
    if nomMonumento in seen_monuments:
        log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Monumento duplicado en la carga actual")
        total_records_rejected += 1
        return False
    
    seen_monuments.add(nomMonumento)

    # Si estamos en la segunda validación después de Location Finder, solo validamos sin escribir logs
    if pasadoPorLocationFinder:
        # Verificar que las coordenadas tengan valor
        if coordenadas_null(latitud, longitud):
            return False

        # Verificar que las coordenadas estén dentro del rango
        if fuente == "XML" or fuente == "JSON":
            if coordenadas_fuera_de_rango(latitud, longitud, fuente):
                return False
        
        if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
            return False

        # Verificar que la provincia esté bien escrita
        if provincia_incorrecta(nomProvincia, fuente):
            return False
        
        # Verificar que la provincia tiene las tildes correctas
        if provincia_sin_tilde(nomProvincia, fuente):
            return True
        
        # Verificar código postal
        if cp_null(codigoPostal, fuente) or str(codigoPostal).upper() == 'N/A':
            borrar_linea_log(fuente, nomMonumento, nomLocalidad, "Código postal sin valor")
            log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Código postal sin valor o N/A, no se ha podido reparar")
            total_records_rejected += 1
            total_records_repaired -= 1
            total_records_added_correctly -= 1
            return False

        # Verificar dirección
        if direccion_null(direccion, fuente, pasadoPorLocationFinder):
            borrar_linea_log(fuente, nomMonumento, nomLocalidad, "Dirección sin valor")
            log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Dirección sin valor")
            total_records_rejected += 1
            total_records_repaired -= 1
            total_records_added_correctly -= 1
            return False

        return True

    # Primera validación - escribir logs normalmente
    # Verificar que las coordenadas tengan valor
    if coordenadas_null(latitud, longitud):
        log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Coordenadas sin valor")
        total_records_rejected += 1
        return False

    # Verificar que las coordenadas estén dentro del rango
    if fuente == "XML" or fuente == "JSON":
        if coordenadas_fuera_de_rango(latitud, longitud, fuente):
            log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Coordenadas fuera de rango")
            total_records_rejected += 1
            return False
    
    if not validar_provincia_localidad(nomLocalidad, tipo="localidad"):
        log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Localidad inválida")
        total_records_rejected += 1
        return False

    # Verificar que la provincia esté bien escrita
    if provincia_incorrecta(nomProvincia, fuente):
        log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Provincia inválida")
        total_records_rejected += 1
        return False
    
    # Verificar que la provincia tiene las tildes correctas
    if provincia_sin_tilde(nomProvincia, fuente):
        log_repair(logger_reparados, fuente, nomMonumento, nomLocalidad, "Provincia sin tilde", "Agregar la tilde")
        total_records_repaired += 1
        return True
    
    # Verificar código postal
    if cp_null(codigoPostal, fuente) or str(codigoPostal).upper() == 'N/A':
        log_repair(logger_reparados, fuente, nomMonumento, nomLocalidad, "Código postal sin valor o N/A", "Búsqueda del código postal con Location Finder")
        total_records_repaired += 1
        return True
    
    # Verificar que el código postal tenga 4 dígitos
    if cp_de_4_digitos(codigoPostal, fuente) == -1:
        log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Código postal con menos de 4 digitos")
        total_records_rejected += 1
        return False
    
    if cp_de_4_digitos(codigoPostal, fuente) == 1:
        log_repair(logger_reparados, fuente, nomMonumento, nomLocalidad, "Código postal con menos de 5 digitos", "Reparado mediante la adición de 0 a la izquierda")
        total_records_repaired += 1
        return True
    
    # Verificar que el código postal esté dentro del rango
    if cp_fuera_de_rango(codigoPostal, fuente):
        log_error(logger_rechazados, fuente, nomMonumento, nomLocalidad, "Código postal fuera de rango")
        total_records_rejected += 1
        return False
    
    # Verificar dirección
    if direccion_null(direccion, fuente, pasadoPorLocationFinder):
        log_repair(logger_reparados, fuente, nomMonumento, nomLocalidad, "Dirección sin valor", "Búsqueda de la dirección con Location Finder")
        total_records_repaired += 1
        return True

    return True


def get_total_records_added_correctly():
    """
    Devuelve el número total de registro cargados correctamente.
    """
    return total_records_added_correctly

def log_statistics():
    """
    Registra las estadísticas generales en el archivo de log.
    """
    global total_records_added_correctly, total_records_rejected, total_records_repaired
    
    logger_estadisticas = logging.getLogger(f'estadisticas_{data_source}')
    if hasattr(sys.modules['__main__'], 'num_monumentos'):
        logger_estadisticas.info(f"Número total de monumentos en el archivo: {sys.modules['__main__'].num_monumentos}")
    total_datos = total_records_added_correctly + total_records_rejected
    logger_estadisticas.info(f"Total de datos procesados: {total_datos}")
    logger_estadisticas.info(f"Total de registros cargados correctamente: {total_records_added_correctly - total_records_repaired}")
    logger_estadisticas.info(f"Total de registros rechazados: {total_records_rejected}")
    logger_estadisticas.info(f"Total de registros reparados: {total_records_repaired}")
    
    # Reiniciar contadores
    total_records_added_correctly = 0
    total_records_rejected = 0
    total_records_repaired = 0

def is_duplicate_monument(nomMonumento, seen_monuments):
    """
    Verifica si un monumento está duplicado, ya sea en la lista actual o en la base de datos.
    """
    from SQL.BDConnection import BDConnection

    # Verificar si está en la lista actual de monumentos vistos
    if nomMonumento in seen_monuments:
        return True

    # Verificar si existe en la base de datos
    try:
        bd_connection = BDConnection()
        bd_connection.init_db("carga")
        existing_monuments = bd_connection.get_existing_monuments()
        bd_connection.close()

        # Comparar con los monumentos existentes
        for monument in existing_monuments:
            if monument.nombre.lower() == nomMonumento.lower():
                return True
    except Exception as e:
        print(f"Error al verificar duplicados en la base de datos: {str(e)}")

    # Si no está duplicado, agregarlo a la lista de vistos
    seen_monuments.add(nomMonumento)
    return False
