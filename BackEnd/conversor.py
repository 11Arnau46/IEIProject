import csv
import json

# Archivo CSV de entrada y archivo JSON de salida
csv_file = 'archivo.csv'
json_file = 'archivo.json'

# Lista para almacenar los datos del CSV
data = []

# Leer el archivo CSV
with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        data.append(row)  # Agregar cada fila como un diccionario a la lista

# Escribir los datos en un archivo JSON
with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)

print(f"Archivo JSON generado: {json_file}")
