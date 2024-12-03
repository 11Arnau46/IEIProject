import json
from sqlalchemy.orm import Session
from SQL.BDMap import Provincia, Localidad, Monumento, TipoMonumento
from enum import Enum

def cargar_datos(session: Session, filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        data = json.load(file)
        for item in data:
            # Buscar o crear la provincia
            provincia = session.query(Provincia).filter_by(nombre=item["nomProvincia"]).first()
            if not provincia:
                provincia = Provincia(
                    nombre=item["nomProvincia"],
                    codigo=item.get("codProvincia")
                )
                session.add(provincia)

            # Buscar o crear la localidad
            localidad = session.query(Localidad).filter_by(nombre=item["nomLocalidad"]).first()
            if not localidad:
                localidad = Localidad(
                    nombre=item["nomLocalidad"],
                    codigo=item.get("codLocalidad"),
                    en_provincia=provincia.id  # Asignar la provincia a la localidad
                )
                session.add(localidad)

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

        # Guardar los cambios
        session.commit()
