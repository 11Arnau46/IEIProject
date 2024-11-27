""" import pandas as pd

# Leer el archivo JSON
json_path = '../Fuentes_de_datos/Euskadi/eus.json'
df = pd.read_json(json_path, delimiter=';', encoding='utf-8')

# Convertir JSON en DataFrame
df = pd.DataFrame(data)

# Seleccionar columnas específicas que deseas extraer
columns_to_extract = [
    "documentName",
    "documentDescription",
    "templateType",
    "locality",
    "address",
    "postalCode",
    "latitudelongitude",
    "municipality",
    "territory"
]
extracted_data = df[columns_to_extract]

# Convertir DataFrame en JSON
new_json = extracted_data.to_json(orient="records", indent=4, force_ascii=False)

# Guardar el nuevo JSON en un archivo
output_file = "extracted_data.json"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(new_json)

print(f"Nuevo archivo JSON guardado en {output_file}")  """

import pandas as pd
import json

# Ruta del archivo JSON
json_path = '../Fuentes_de_datos/Euskadi/eus.json'

# Leer el archivo JSON como un diccionario
with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

# Aplanar los datos usando pandas.json_normalize
df = pd.json_normalize(data)

# Seleccionar columnas específicas que deseas extraer
columns_to_extract = [
    "documentName",
    "documentDescription",
    "templateType",
    "locality",
    "address",
    "postalCode",
    "latitudelongitude",
    "municipality",
    "territory"
]
extracted_data = df[columns_to_extract]

# Convertir DataFrame a JSON
new_json = extracted_data.to_json(orient="records", indent=4, force_ascii=False)

# Guardar el nuevo JSON en un archivo
output_file = "extracted_data.json"
with open(output_file, "w", encoding="utf-8") as file:
    file.write(new_json)

print(f"Nuevo archivo JSON guardado en {output_file}")