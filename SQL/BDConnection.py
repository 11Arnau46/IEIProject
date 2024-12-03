from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from SQL.BDMap import Base  # Importa Base desde el archivo de modelos

# Configuración de la conexión a la base de datos:   usuario:contraseña
DATABASE_URI = 'mysql+mysqlconnector://root:123456@127.0.0.1:3306/IEI'

# Crear el motor de SQLAlchemy
engine = create_engine(DATABASE_URI, echo=True)

# Crear la fábrica de sesiones
Session = sessionmaker(bind=engine)

# Crear las tablas si no existen
def init_db():
    # Elimina todas las tablas existentes
    Base.metadata.drop_all(engine)
    print("Tablas eliminadas.")

    # Crea las tablas desde cero
    Base.metadata.create_all(engine)
    print("Tablas creadas exitosamente.")