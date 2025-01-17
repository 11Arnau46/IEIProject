import xmltodict
import json
import os

from BackEnd.config.paths import INPUT_XML_PATH
def XMLtoJSON():
    # Obtener la ruta del directorio raíz y actual
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

    # Crear la ruta completa hacia "Fuente_de_datos/Final/vcl.csv"
    path_archivo_gen = os.path.abspath(os.path.join(BASE_DIR, 'BackEnd', 'Wrappers', 'XMLtoJSON.json'))

    # Leer el archivo XML con la codificación utf-8
    with open(INPUT_XML_PATH, 'r', encoding='utf-8') as xml_file:
        xml_data = xmltodict.parse(xml_file.read())

    # Convertir el diccionario a JSON sin escapar caracteres no ASCII
    with open(path_archivo_gen, 'w', encoding='utf-8') as json_file:
        json.dump(xml_data, json_file, indent=4, ensure_ascii=False)