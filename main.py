import sys
import subprocess
from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos

def ejecutar_extractor(tipo):
    if tipo == "csv":
        subprocess.run(["py", "BackEnd/Extractor_CSV.py"])
        return "Resultados/CSVtoJSON_Corregido.json"
    elif tipo == "json":
        subprocess.run(["py", "BackEnd/Extractor_JSON.py"])
        return "Resultados/JSONtoJSON_con_coords.json"
    elif tipo == "xml":
        subprocess.run(["py", "BackEnd/Extractor_XML.py"])
        return "Resultados/XMLtoJSON_con_coords.json"
    else:
        raise ValueError("Tipo de extractor no válido. Use 'csv', 'json' o 'xml'.")

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