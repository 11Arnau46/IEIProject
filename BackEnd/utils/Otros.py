def process_and_save_json(json_path):
    location_finder = LocationFinder(json_path)
    # Procesar el JSON y obtener los resultados
    results = location_finder.process_json()
    # Guardar los resultados en el archivo
    location_finder.save_results_to_json(results)
    print(f"Archivo final guardado en {json_path}.")

def aplicar_filtros_estandar(df):
    """
    Aplica los filtros estandarizados a las columnas específicas de un DataFrame.
    
    Argumentos:
        df (pd.DataFrame): DataFrame al que se le aplicarán los filtros.

    Retorna:
        pd.DataFrame: DataFrame con los filtros aplicados.
    """
    from utils.filtros import clean_coordinates, limpiar_campo_duplicado  # Asegúrate de importar las funciones necesarias
    
    # Diccionario con columnas y sus funciones de filtro
    filtros = {
        'latitud': clean_coordinates,
        'longitud': clean_coordinates,
        'codLocalidad': limpiar_campo_duplicado,
        'nomLocalidad': limpiar_campo_duplicado,
        'codProvincia': limpiar_campo_duplicado,
        'nomProvincia': limpiar_campo_duplicado,
    }

    # Aplicar los filtros
    for columna, filtro in filtros.items():
        if columna in df.columns:  # Verifica si la columna existe en el DataFrame
            df[columna] = df[columna].apply(filtro)
    
    return df
