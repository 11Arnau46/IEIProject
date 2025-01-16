import os
import sys
import subprocess
from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos
from BackEnd.utils.Otros import set_data_source, setup_loggers
from BackEnd.Wrappers.Wrapper_CSV import process_csv
from BackEnd.Wrappers.Wrapper_JSON import process_json
from BackEnd.Wrappers.Wrapper_XML import process_xml
from SQL.BDMap import Provincia, Localidad, Monumento, TipoMonumento
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

class SQL:
    def __init__(self):
        self.initialize_db()  # Llamar automáticamente al método al inicializar la clase

    def initialize_db(self):
        # Crear la instancia de BDConnection
        bd_connection = BDConnection()

        # Inicializar la base de datos
        engine_with_db = bd_connection.init_db()  # Aquí se obtiene el engine conectado a 'IEI'
    
        if engine_with_db is None:
            print("Error al inicializar la base de datos. Terminando el proceso.")
            return

        # Crear una sesión de base de datos usando el engine con la base de datos seleccionada
        self.session = bd_connection.session  # Guardar la sesión como atributo de la clase
    
    def cargar_datos(self, data):
        session = self.session
        
        for item in data:
            try:
                # Buscar o crear la provincia
                provincia = session.query(Provincia).filter_by(nombre=item["nomProvincia"]).first()
                if not provincia:
                    provincia = Provincia(
                        nombre=item["nomProvincia"],
                    )
                    session.add(provincia)
                    session.flush()  # Forzar ID de provincia antes de usarla en localidad

                # Buscar o crear la localidad
                localidad = session.query(Localidad).filter_by(nombre=item["nomLocalidad"]).first()
                if not localidad:
                    localidad = Localidad(
                        nombre=item["nomLocalidad"],
                        en_provincia=provincia.id  # Asignar la provincia a la localidad
                    )
                    session.add(localidad)
                    session.flush()  # Forzar ID de localidad antes de usarla en monumento

                # Asignar el tipo de monumento usando el Enum
                tipo_monumento = TipoMonumento[item["tipoMonumento"]] if item["tipoMonumento"] in TipoMonumento.__members__ else TipoMonumento.Otros

                # Crear el monumento
                monumento = Monumento(
                    nombre=item["nomMonumento"],
                    tipo=tipo_monumento,
                    direccion=item.get("direccion"),
                    codigo_postal=item.get("codigo_postal"),
                    longitud=item.get("longitud"),
                    latitud=item.get("latitud"),
                    descripcion=item.get("descripcion"),
                    en_localidad=localidad.id  # Asignar la localidad al monumento
                )
                session.add(monumento)

                # Confirmar los cambios para este lote
                session.commit()

            except SQLAlchemyError as e:
                # Revertir cualquier cambio si ocurre un error
                session.rollback()

                # Mostrar la información del error y el objeto problemático
                print(f"Error al procesar el item: {item}")
                print(f"Error SQLAlchemy: {str(e)}")

            except Exception as e:
                # Capturar cualquier otro error no relacionado con SQLAlchemy
                session.rollback()
                print(f"Error inesperado al procesar el item: {item}")
                print(f"Error: {str(e)}")
