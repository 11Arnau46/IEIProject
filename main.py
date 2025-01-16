import os
import sys
import subprocess
from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos
from BackEnd.utils.Otros import set_data_source, setup_loggers
from BackEnd.Wrappers.Wrapper_CSV import process_csv
from BackEnd.Wrappers.Wrapper_JSON import process_json
from BackEnd.Wrappers.Wrapper_XML import process_xml


def ejecutar_wrapper(tipo):
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    if tipo == "csv":
        process_csv() 
        result_file = os.path.join(current_dir, "Resultados", "CSVtoJSON_Corregido.json")
        return result_file
    elif tipo == "json":
        process_json()
        result_file = os.path.join(current_dir, "Resultados", "JSONtoJSON_con_coords.json")
        return result_file
    elif tipo == "xml":
        process_xml()
        result_file = os.path.join(current_dir, "Resultados", "XMLtoJSON_con_coords.json")
        return result_file
    else:
        raise ValueError("Tipo de extractor no válido. Use 'csv', 'json' o 'xml'.")
    
def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <tipo_wrapper>")
        print("Tipos válidos: csv, json, xml")
        return

    tipo_wrapper = sys.argv[1]
    
    # Establecer la fuente de datos global
    set_data_source(tipo_wrapper)
    
    # Configurar los loggers
    setup_loggers(tipo_wrapper)

    try:
        # Ejecutar el extractor correspondiente
        json_path = ejecutar_wrapper(tipo_wrapper)

        # Crear la instancia de BDConnection
        bd_connection = BDConnection()

        # Inicializar la base de datos
        engine_with_db = bd_connection.init_db("carga")  # Aquí se obtiene el engine conectado a 'IEI'

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