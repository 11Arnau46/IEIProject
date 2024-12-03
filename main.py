from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos

def main():
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
        cargar_datos(session, "Resultados/JSONtoJSON.json")
        print("Datos cargados exitosamente en la base de datos.")
    except Exception as e:
        print(f"Error al cargar datos: {e}")
    finally:
        bd_connection.close()  # Cerrar la sesión al final

if __name__ == "__main__":
    main()
