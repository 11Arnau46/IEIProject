import os

# Función para obtener la ruta relativa a BASE_DIR o para usar una ruta completa
def get_relative_path(*path_parts, use_base_dir=True):
    if use_base_dir:
        # Añadir '..' al principio para subir un nivel
        return os.path.join(BASE_DIR, '..', *path_parts)
    else:
        # Añadir '..' al principio para rutas relativas
        return os.path.join('..', *path_parts)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Rutas con BASE_DIR (relativas)
INPUT_CSV_PATH = get_relative_path('..', 'Fuentes_de_datos', 'Demo', 'vcl.csv', use_base_dir=False)
INPUT_JSON_PATH = get_relative_path('..', 'Fuentes_de_datos', 'Demo', 'eus.json', use_base_dir=False)
INPUT_XML_PATH = get_relative_path('..', 'Fuentes_de_datos', 'Demo', 'cle.xml', use_base_dir=False)

