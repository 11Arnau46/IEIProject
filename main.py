from SQL.BDConnection import Session, init_db
from SQL.Json_Loader import cargar_datos

def main():
    # Inicializar la base de datos
    init_db()

    # Crear una sesión de base de datos
    session = Session()

    try:
        # Cargar datos desde el archivo JSON
        cargar_datos(session, "Resultados/CSVtoJSON_con_coords.json")
        print("Datos cargados exitosamente en la base de datos.")
    except Exception as e:
        print(f"Error al cargar datos: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()
