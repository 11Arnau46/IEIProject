import os

# Función para obtener la ruta relativa a BASE_DIR o para usar una ruta completa
def get_relative_path(*path_parts, use_base_dir=True):
    if use_base_dir:
        return os.path.join(BASE_DIR, *path_parts)
    else:
        return os.path.join(*path_parts)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas con BASE_DIR (relativas)
INPUT_CSV_PATH = get_relative_path('Fuentes_de_datos', 'Demo', 'vcl.csv')
INPUT_JSON_PATH = get_relative_path('Fuentes_de_datos', 'Demo', 'eus.json')
INPUT_XML_PATH = get_relative_path('Fuentes_de_datos', 'Demo', 'cle.xml')

# Rutas de salida
OUTPUT_CSV_PATHS = {
    'with_coords': get_relative_path('Resultados', 'CSVtoJSON_con_coords.json'),
    'without_coords': get_relative_path('Resultados', 'CSVtoJSON_sin_coords.json'),
    'corrected_coords': get_relative_path('Resultados', 'CSVtoJSON_Corregido.json')
}

OUTPUT_JSON_PATHS = {
    'with_coords': get_relative_path('Resultados', 'JSONtoJSON_con_coords.json'),
    'without_coords': get_relative_path('Resultados', 'JSONtoJSON_sin_coords.json'),
    'corrected_coords': get_relative_path('Resultados', 'JSONtoJSON_Corregido.json')
}

OUTPUT_XML_PATHS = {
    'with_coords': get_relative_path('Resultados', 'XMLtoJSON_con_coords.json'),
    'without_coords': get_relative_path('Resultados', 'XMLtoJSON_sin_coords.json'),
    'corrected_coords': get_relative_path('Resultados', 'XMLtoJSON_Corregido.json')
}
