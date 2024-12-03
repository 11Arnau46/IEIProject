import requests

# Endpoint de la API
url = "https://api.geoapify.com/v1/geocode/reverse"
params = {
    "lat": 38.94391169,
    "lon": -0.44372005,
    "apiKey": "3b3eb29261ae4a61bd9fc55c2e50f74d"
}

# Realiza la solicitud
response = requests.get(url, params=params)

# Convierte la respuesta a JSON
data = response.json()

# Extrae el 'postcode' y 'street' del primer elemento en 'features'
if data.get("features"):
    feature = data["features"][0]  # Primer resultado
    properties = feature.get("properties", {})
    postcode = properties.get("postcode", "No encontrado")
    street = properties.get("street", "No encontrado")

    print(f"Código postal: {postcode}")
    print(f"Calle: {street}")
else:
    print("No se encontraron datos en la respuesta.")

    

def obtener_codigo_postal_y_calle(lat, lon):
    """
    Dado unas coordenadas (latitud y longitud), obtiene el código postal y la calle usando Geoapify API.

    Args:
        lat (float): Latitud de la ubicación.
        lon (float): Longitud de la ubicación.

    Returns:
        tuple: Una tupla con el código postal y la calle (postcode, street). Si no se encuentran datos, devuelve ("No encontrado", "No encontrado").
    """
    # Endpoint y parámetros
    url = "https://api.geoapify.com/v1/geocode/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "apiKey": "3b3eb29261ae4a61bd9fc55c2e50f74d"
    }

    try:
        # Realizar la solicitud
        response = requests.get(url, params=params)
        response.raise_for_status()  # Lanza excepción si hay error HTTP

        # Procesar la respuesta JSON
        data = response.json()
        if data.get("features"):
            properties = data["features"][0].get("properties", {})
            postcode = properties.get("postcode", "No encontrado")
            street = properties.get("street", "No encontrado")
            return postcode, street
        else:
            return "No encontrado", "No encontrado"
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar la solicitud: {e}")
        return "Error", "Error"
