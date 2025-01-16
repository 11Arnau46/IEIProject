import xmltodict
import json
import os

def XMLtoJSON():
    # Obtener la ruta del directorio raíz y actual
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

    # Crear la ruta completa hacia "Fuente_de_datos/Final/vcl.csv"
    path = os.path.abspath(os.path.join(BASE_DIR, 'Fuentes_de_datos', 'Final', 'cle.xml'))


    # Leer el archivo XML con la codificación utf-8
    with open('E:\Coding\IEI Proyecto\IEIProject\Fuentes_de_datos\Final\cle.xml', 'r', encoding='utf-8') as xml_file:
        xml_data = xmltodict.parse(xml_file.read())

    # Convertir el diccionario a JSON sin escapar caracteres no ASCII
    with open('XMLtoJSON.json', 'w', encoding='utf-8') as json_file:
        json.dump(xml_data, json_file, indent=4, ensure_ascii=False)