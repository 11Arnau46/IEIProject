import csv
import json
import sys
import os
from pathlib import Path

# Obtener la ruta del directorio raíz y actual
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

# Crear la ruta completa hacia "Fuente_de_datos/Final/vcl.csv"
path = os.path.abspath(os.path.join(BASE_DIR, 'Fuentes_de_datos', 'Final', 'vcl.csv'))

# Leer el archivo CSV con la codificación utf-8 y delimitador ';'
with open(path, 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.DictReader(csv_file, delimiter=';')  # Usar ';' como delimitador
    data = list(csv_reader)  # Convertir el lector a lista de diccionarios

# Escribir el archivo JSON sin escapar caracteres no ASCII
with open('CSVtoJSON.json', 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, indent=4, ensure_ascii=False)