import sys
from pathlib import Path
from flask import Flask, Response, request, jsonify
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError  # Import SQLAlchemyError

# Add the root project directory to the Python path
root_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(root_dir))

from SQL.BDConnection import BDConnection

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

api = Api(app)

# Swagger UI configuration
SWAGGER_URL = '/swagger-ui'
API_URL = '/static/swagger.json'  # Path to the Swagger JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Búsqueda API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

class GetDataFromDB(Resource):
    def get(self):
        bd_connection = BDConnection()
        bd_connection.init_db("busqueda")  # Ensure the session is initialized
        session = bd_connection.session

        if session is None:
            return {"error": "Failed to connect to the database."}, 500

        # Get query parameters
        localidad = request.args.get('localidad')
        codigo_postal = request.args.get('codigo_postal')
        provincia = request.args.get('provincia')
        tipo = request.args.get('tipo')

        query = """
        SELECT 
            monumento.nombre AS nombre_monumento,
            monumento.tipo AS tipo_monumento,
            monumento.direccion AS direccion,
            localidad.nombre AS nombre_localidad,
            monumento.codigo_postal AS codigo_postal,
            provincia.nombre AS nombre_provincia,
            monumento.descripcion AS descripcion,
            monumento.latitud AS latitud,
            monumento.longitud AS longitud
        FROM monumento
        JOIN localidad ON monumento.en_localidad = localidad.id
        JOIN provincia ON localidad.en_provincia = provincia.id
        WHERE 1=1
        """
        params = {}

        if localidad:
            query += " AND localidad.nombre = :localidad"
            params['localidad'] = localidad
        if codigo_postal:
            query += " AND monumento.codigo_postal = :codigo_postal"
            params['codigo_postal'] = codigo_postal
        if provincia:
            query += " AND provincia.nombre = :provincia"
            params['provincia'] = provincia
        if tipo:
            query += " AND monumento.tipo = :tipo"
            params['tipo'] = tipo

        try:
            print(f"Executing query: {query} with params: {params}")
            
            # Execute the query with parameters if they exist
            if params:
                data = session.execute(text(query), params).mappings().fetchall()
            else:
                # If no params, execute the query without them
                data = session.execute(text(query)).mappings().fetchall()

            # Close the connection in a finally block
            bd_connection.close()

            if not data:
                return {"error": "No se encontraron monumentos para los filtros especificados."}, 404

            # Convert RowMapping to dictionary
            result = [
                {
                    "nombre_monumento": row["nombre_monumento"],
                    "tipo_monumento": row["tipo_monumento"],
                    "direccion": row["direccion"],
                    "nombre_localidad": row["nombre_localidad"],
                    "codigo_postal": row["codigo_postal"],
                    "nombre_provincia": row["nombre_provincia"],
                    "descripcion": row["descripcion"],
                    "latitud": row["latitud"],
                    "longitud": row["longitud"]
                }
                for row in data
            ]
            print(f"Query result: {result}")

            # Return results directly
            return result, 200
        except SQLAlchemyError as e:
            print(f"SQLAlchemyError: {e}")
            bd_connection.close()
            return {"error": "Error interno del servidor. Intente más tarde."}, 500
        except Exception as e:
            print(f"Unexpected Error: {e}")
            bd_connection.close()
            return {"error": "Error inesperado. Intente más tarde."}, 500



# Add the resource to the API
api.add_resource(GetDataFromDB, '/api/monumentos')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
