import json
import os

def JSONtoJSON():
    # Obtener la ruta del directorio raíz y actual
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

    # Crear la ruta completa hacia "Fuente_de_datos/Final/vcl.csv"
    path = os.path.abspath(os.path.join(BASE_DIR, 'Fuentes_de_datos', 'Final', 'eus.json'))
    path2 = os.path.abspath(os.path.join(BASE_DIR, 'BackEnd', 'Wrappers', 'JSONtoJSON.json'))

    # Leer el archivo JSON
    with open(path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)  # Cargar el contenido del JSON en un diccionario

    # Realizar alguna modificación, si es necesario. Por ejemplo, se podría cambiar el contenido:
    # data['nuevo_campo'] = 'valor'

    # Escribir el archivo JSON modificado
    with open(path2, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)