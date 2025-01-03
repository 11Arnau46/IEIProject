from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .BDMap import Base  # Importación relativa al paquete actual

class BDConnection:
    def __init__(self, usuario='root', contrasena='123456', host='127.0.0.1', puerto=3306, db_name='IEI'):
        self.usuario = usuario
        self.contrasena = contrasena
        self.host = host
        self.puerto = puerto
        self.db_name = db_name
        self.engine = None
        self.session = None

    def create_engine_without_db(self):
        """ Crea un motor de SQLAlchemy sin base de datos especificada """
        return create_engine(f'mysql+mysqlconnector://{self.usuario}:{self.contrasena}@{self.host}:{self.puerto}/', echo=False)

    def create_engine_with_db(self):
        """ Crea un motor de SQLAlchemy con la base de datos especificada """
        return create_engine(f'mysql+mysqlconnector://{self.usuario}:{self.contrasena}@{self.host}:{self.puerto}/{self.db_name}', echo=False)

    def drop_database_if_exists(self):
        """ Elimina la base de datos si existe """
        try:
            engine_no_db = self.create_engine_without_db()
            with engine_no_db.connect() as conn:
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.db_name}"))
                conn.commit()
        except OperationalError as e:
            print(f"Error al intentar eliminar la base de datos: {e}")
            raise

    def create_database_if_not_exists(self):
        """ Crear la base de datos si no existe """
        try:
            # Usamos el motor sin base de datos especificada para verificar la existencia
            engine_no_db = self.create_engine_without_db()
            with engine_no_db.connect() as conn:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.db_name}"))
                conn.commit()
        except OperationalError as e:
            print(f"Error al intentar conectar con la base de datos: {e}")
            raise

    def init_db(self):
        """ Inicializa la base de datos y crea las tablas si es necesario """
        try:
            # Primero, eliminar la base de datos si existe
            self.drop_database_if_exists()
            
            # Luego, crear la base de datos
            self.create_database_if_not_exists()

            # Ahora creamos el motor conectado a la base de datos
            self.engine = self.create_engine_with_db()

            # Crear las tablas
            Base.metadata.create_all(self.engine)
            print("Tablas creadas exitosamente.")
            
            # Crear la sesión
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            return self.engine  # Devolver el motor para usar en otros lugares

        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")
            return None
    
    def close(self):
        """ Cerrar la sesión si existe """
        if self.session:
            self.session.close()
            print("Sesión cerrada correctamente.")
    
# Uso de la clase BDConnection
if __name__ == "__main__":
    bd_connection = BDConnection()
    engine = bd_connection.init_db()
    
    if engine:
        print("Conexión y base de datos inicializada correctamente.")
    else:
        print("Hubo un error al conectar con la base de datos.")
    
    # Cerrar la conexión cuando ya no sea necesaria
    bd_connection.close()
