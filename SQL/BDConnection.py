from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .BDMap import Base  # Importación relativa al paquete actual

class BDConnection:
    def __init__(self, contrasena=None):
        self.usuario = 'root'
        self.contrasena = None
        self.host = '127.0.0.1'
        self.puerto = 3306
        self.db_name = 'IEI'
        self.engine = None
        self.session = None

    def try_connection(self):
        """ Intenta crear una conexión probando diferentes contraseñas """
        passwords = ['root', 'password', '1234', '123456']
        
        for password in passwords:
            try:
                engine = create_engine(f'mysql+mysqlconnector://{self.usuario}:{password}@{self.host}:{self.puerto}/', echo=False)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    print(f"¡Conexión exitosa!")
                    self.contrasena = password
                    return True
            except Exception:
                continue
        
        return False

    def init_db(self, accion):
        """ Inicializa la base de datos y crea las tablas si es necesario """
        try:
            # Intentar establecer la conexión
            if not self.try_connection():
                raise Exception("No se pudo conectar con ninguna de las contraseñas disponibles")
            
            if accion == "carga":
                print("\nConectando a la base de datos...")
                # Crear la base de datos si no existe
                engine_no_db = self.create_engine_without_db()
                with engine_no_db.connect() as conn:
                    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.db_name}"))
                    conn.commit()
                    print(f"Base de datos {self.db_name} creada si no existía")

                # Ahora creamos el motor conectado a la base de datos
                self.engine = self.create_engine_with_db()

                # Crear las tablas si no existen
                Base.metadata.create_all(self.engine)
                print("Tablas creadas si no existían")
                
            elif accion == "busqueda":
                print("\nConectando a la base de datos existente...")
                # Ahora creamos el motor conectado a la base de datos
                self.engine = self.create_engine_with_db()
            
            # Crear la sesión
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            print("Sesión creada exitosamente")
            return self.engine

        except Exception as e:
            print(f"\nError al inicializar la base de datos: {str(e)}")
            raise

    def create_engine_without_db(self):
        """ Crea un motor de SQLAlchemy sin base de datos especificada """
        return create_engine(f'mysql+mysqlconnector://{self.usuario}:{self.contrasena}@{self.host}:{self.puerto}/', echo=False)

    def create_engine_with_db(self):
        """ Crea un motor de SQLAlchemy con la base de datos especificada """
        return create_engine(f'mysql+mysqlconnector://{self.usuario}:{self.contrasena}@{self.host}:{self.puerto}/{self.db_name}', echo=False)

    def close(self):
        """ Cerrar la sesión si existe """
        if self.session:
            self.session.close()
            print("Sesión cerrada correctamente")

    def get_existing_monuments(self):
        """ Obtiene todos los monumentos existentes en la base de datos """
        from .BDMap import Monumento
        if self.session:
            return self.session.query(Monumento).all()
        return []

# Uso de la clase BDConnection
if __name__ == "__main__":
    bd_connection = BDConnection()
    engine = bd_connection.init_db("carga")
    
    if engine:
        print("Conexión y base de datos inicializada correctamente.")
    else:
        print("Hubo un error al conectar con la base de datos.")
    
    # Cerrar la conexión cuando ya no sea necesaria
    bd_connection.close()
