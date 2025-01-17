import json
import os

def JSONtoJSON():
    # Obtener la ruta del directorio raíz y actual
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    BASE_DIR = os.path.dirname(os.path.dirname(CURRENT_DIR))

    # Crear las rutas completas
    input_path = os.path.abspath(os.path.join(BASE_DIR, 'Fuentes_de_datos', 'Final', 'eus.json'))
    output_path = os.path.abspath(os.path.join(BASE_DIR, 'BackEnd', 'Wrappers', 'JSONtoJSON.json'))

    # Leer el archivo como texto para procesar manualmente las claves duplicadas
    with open(input_path, 'r', encoding='utf-8') as json_file:
        content = json_file.read()
        monuments = []
        current_monument = []
        in_monument = False
        
        # Dividir el contenido en líneas y procesar cada línea
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('{'):
                in_monument = True
                current_monument = []
            elif line.startswith('}'):
                if current_monument:
                    # Procesar el monumento actual
                    field_values = {}
                    processed_monument = {}
                    
                    for field in current_monument:
                        key = field['key']
                        value = field['value']
                        
                        if key not in field_values:
                            # Primera aparición del campo
                            field_values[key] = value
                            processed_monument[key] = value
                        elif not field_values[key] and value:
                            # Si el valor guardado está vacío y el nuevo tiene contenido
                            field_values[key] = value
                            processed_monument[key] = value
                    
                    monuments.append(processed_monument)
                in_monument = False
            elif in_monument and '"' in line and ':' in line:
                # Extraer clave y valor
                key = line.split('"')[1]
                value = line.split(':')[1].strip().strip(',').strip('"')
                current_monument.append({'key': key, 'value': value})

    # Guardar el resultado en un archivo JSON
    with open(output_path, 'w', encoding='utf-8') as output_file:
        json.dump(monuments, output_file, indent=4, ensure_ascii=False)
