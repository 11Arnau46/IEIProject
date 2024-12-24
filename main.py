import sys
import subprocess
from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos
import os

# Función para ejecutar el extractor y generar el archivo correspondiente
def ejecutar_extractor(tipo):
    # Definir la ruta del archivo corregido según el tipo
    if tipo == "csv":
        # Ejecutar el script para CSV
        subprocess.run(["python3", "BackEnd/Extractor_CSV.py"])
        json_path = "Resultados/CSVtoJSON_Corregido.json"
    elif tipo == "json":
        # Ejecutar el script para JSON
        subprocess.run(["python3", "BackEnd/Extractor_JSON.py"])
        json_path = "Resultados/JSONtoJSON_con_coords.json"
    elif tipo == "xml":
        # Ejecutar el script para XML
        subprocess.run(["python3", "BackEnd/Extractor_XML.py"])
        json_path = "Resultados/XMLtoJSON_con_coords.json"
    else:
        raise ValueError("Tipo de extractor no válido. Use 'csv', 'json' o 'xml'.")
    
    # Comprobar si el archivo ya existe y si es necesario sobreescribir
    if os.path.exists(json_path):
        print(f"El archivo {json_path} ya existe, se sobrescribirá.")
    else:
        print(f"El archivo {json_path} no existe, se creará uno nuevo.")

    return json_path

def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <tipo_extractor>")
        print("Tipos válidos: csv, json, xml")
        return

    tipo_extractor = sys.argv[1]

    try:
        # Ejecutar el extractor correspondiente
        json_path = ejecutar_extractor(tipo_extractor)

        # Crear la instancia de BDConnection
        bd_connection = BDConnection()

        # Inicializar la base de datos
        engine_with_db = bd_connection.init_db()  # Aquí se obtiene el engine conectado a 'IEI'

        if engine_with_db is None:
            print("Error al inicializar la base de datos. Terminando el proceso.")
            return

        # Crear una sesión de base de datos usando el engine con la base de datos seleccionada
        session = bd_connection.session

        try:
            # Cargar datos desde el archivo JSON
            cargar_datos(session, json_path)
            print("Datos cargados exitosamente en la base de datos.")
        except Exception as e:
            print(f"Error al cargar datos: {e}")
        finally:
            bd_connection.close()  # Cerrar la sesión al final

    except ValueError as e:
        print(e)

if __name__ == "__main__":
    main()
