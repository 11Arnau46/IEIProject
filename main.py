import os
import sys
import subprocess
from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos

def get_python_command():
    """Detecta qué comando de Python está disponible en el sistema"""
    try:
        # Intenta primero con 'python'
        subprocess.run(["python", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return "python"
    except FileNotFoundError:
        try:
            # Si 'python' no funciona, intenta con 'python3'
            subprocess.run(["python3", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return "python3"
        except FileNotFoundError:
            raise RuntimeError("No se encontró ninguna instalación de Python válida")

def ejecutar_extractor(tipo):
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    python_cmd = get_python_command()
    
    if tipo == "csv":
        extractor_script = os.path.join(current_dir, "BackEnd", "Extractor_CSV.py")
        result_file = os.path.join(current_dir, "Resultados", "CSVtoJSON_Corregido.json")
        subprocess.run([python_cmd, extractor_script])
        return result_file
    elif tipo == "json":
        extractor_script = os.path.join(current_dir, "BackEnd", "Extractor_JSON.py")
        result_file = os.path.join(current_dir, "Resultados", "JSONtoJSON_con_coords.json")
        subprocess.run([python_cmd, extractor_script])
        return result_file
    elif tipo == "xml":
        extractor_script = os.path.join(current_dir, "BackEnd", "Extractor_XML.py")
        result_file = os.path.join(current_dir, "Resultados", "XMLtoJSON_con_coords.json")
        subprocess.run([python_cmd, extractor_script])
        return result_file
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