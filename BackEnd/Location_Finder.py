import json
import os
import requests
import utm

def get_location_info(lat, lon):
    api_key = 'd5759aade0884056ba8c63a7fe5d9f2f'
    url = f'https://api.opencagedata.com/geocode/v1/json?q={lat}%2C{lon}&key={api_key}'

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['results']:
            components = data['results'][0]['components']
            direction = data['results'][0].get('formatted', 'N/A')
            postal_code = components.get('postcode', 'N/A')
            if postal_code == 'N/A':
                print(f"Missing postcode for {lat}, {lon}: {json.dumps(data, indent=4)}")
            return direction, postal_code
        else:
            return 'N/A', 'N/A'
    else:
        print(f"Error: {response.status_code}")
        return 'N/A', 'N/A'

def process_json(json_path):
    if not os.path.exists(json_path):
        print(f"File not found: {json_path}")
        return []

    with open(json_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    results = []
    for item in data:
        lat = item.get('latitud')
        lon = item.get('longitud')
        if lat and lon:
            direction, postal_code = get_location_info(lat, lon)
            result = {
                'latitud': lat,
                'longitud': lon,
                'direccion': direction,
                'codigo_postal': postal_code
            }
            results.append(result)
            print(result)

    return results

def save_results_to_json(results, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

# Ruta al archivo JSON procesado
json_path = '../Resultados/CSVtoJSON_Corregido.json'
results = process_json(json_path)

# Guardar los resultados en un nuevo archivo JSON
output_path = '../Resultados/processedResults.json'
save_results_to_json(results, output_path)