import json
import requests
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from SQL.BDMap import Provincia, Localidad, Monumento, TipoMonumento

def get_datos():
    """
    Hace una solicitud a la API y guarda la respuesta como un objeto JSON.

    Parámetros:
        api_url (str): La URL de la API que se va a consultar.

    Retorna:
        dict: Los datos procesados como un diccionario Python.
    """

    api_url = "http://localhost:8082/wrapperJSON/execute"

    try:
        # Realizar la solicitud a la API
        response = requests.post(api_url)

        # Verificar si la respuesta es exitosa
        response.raise_for_status()

        # Procesar el contenido de la respuesta como JSON
        data = response.json()

        # Retornar el objeto JSON procesado
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud a la API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al procesar la respuesta como JSON: {e}")
        return None
