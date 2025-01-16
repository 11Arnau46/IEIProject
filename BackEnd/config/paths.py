import os

# Obtener el directorio actual del script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Retroceder dos niveles para llegar a la raíz del proyecto (simulando cd ../..)
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Función para obtener la ruta relativa a BASE_DIR y devolver la ruta completa
def get_relative_path(*path_parts):
    # Combinar BASE_DIR con los fragmentos de ruta proporcionados
    return os.path.abspath(os.path.join(BASE_DIR, *path_parts))

# Rutas completas con BASE_DIR (absolutas)
INPUT_CSV_PATH = get_relative_path('Fuentes_de_datos', 'Final', 'vcl.csv')
INPUT_JSON_PATH = get_relative_path('Fuentes_de_datos', 'Final', 'eus.json')
INPUT_XML_PATH = get_relative_path('Fuentes_de_datos', 'Final', 'cle.xml')

