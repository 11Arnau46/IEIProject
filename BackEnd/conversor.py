import csv
import json
from utms_converter import convert_utm  # Asegúrate de importar la función correctamente

# Archivos de entrada y salida
csv_file = '../Fuentes_de_datos/Comunitat_Valenciana/vcl.csv'
json_file = './Fuentes_de_datos/vlc.json'

# Lista para almacenar los datos filtrados
filtered_data = []

# Leer y procesar el archivo CSV
with open(csv_file, mode='r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file, delimiter=';')
    
    for row in csv_reader:
        # Filtrar los campos no deseados y renombrar los necesarios
        nombre = row['DENOMINACION']
        provincia = row['PROVINCIA']
        municipio = row['MUNICIPIO']
        utm_este = row['UTMESTE']
        utm_norte = row['UTMNORTE']
        
        # Convertir UTM a latitud y longitud
        lat, lon = convert_utm(utm_este, utm_norte)
        
        # Crear un nuevo diccionario con los datos que nos interesan
        new_row = {
            "Nombre": nombre,
            "Provincia": provincia,
            "Municipio": municipio,
            "Latitud": lat,
            "Longitud": lon
        }
        
        filtered_data.append(new_row)

# Guardar los datos filtrados en el archivo JSON
with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(filtered_data, file, indent=4)

print(f"Archivo JSON generado con éxito: {json_file}")
