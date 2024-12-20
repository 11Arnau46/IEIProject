import json
import os
import requests
import time

class LocationFinder:
    def __init__(self, json_path):
        self.json_path = json_path

    def get_location_info(self, lat, lon):
        api_key = 'ab010f03e3d34a31b629db543f088d19' #'d5759aade0884056ba8c63a7fe5d9f2f'
        url1 = f'https://api.opencagedata.com/geocode/v1/json?q={lat}%2C{lon}&key={api_key}'

        response1 = requests.get(url1)

        if response1.status_code == 200:
            data1 = response1.json()
            if data1['results']:
                components = data1['results'][0]['components']
                direction = data1['results'][0].get('formatted', 'N/A')
                postal_code = components.get('postcode', 'N/A')

                if postal_code == 'N/A':
                    api2_key = '3b3eb29261ae4a61bd9fc55c2e50f74d'
                    url2 = f'https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lon}&apiKey={api2_key}'
                    response2 = requests.get(url2)

                    if response2.status_code == 200:
                        data2 = response2.json()
                        if data2['features']:
                            postal_code = data2['features'][0]['properties'].get('postcode', 'N/A')
                return direction, postal_code
            else:
                return 'N/A', 'N/A'
        else:
            return 'N/A', 'N/A'

    def process_json(self):
        if not os.path.exists(self.json_path):
            return []

        with open(self.json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        results = []
        for item in data:
            lat = item.get('latitud')
            lon = item.get('longitud')
            if lat and lon:
                direction, postal_code = self.get_location_info(lat, lon)
                item['direccion'] = direction
                item['codigo_postal'] = postal_code
                results.append(item)

        return results

    def save_results_to_json(self, results):
        with open(self.json_path, 'w', encoding='utf-8') as file:
            json.dump(results, file, ensure_ascii=False, indent=4)