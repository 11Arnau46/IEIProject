from flask import Flask, request, jsonify, send_from_directory
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os
import sys
import logging
from pathlib import Path

# Configuración básica de logging
logging.basicConfig(level=logging.DEBUG)

# Define the root project directory
root_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(root_dir))

from BackEnd.Extractores import Extractor_JSON
from BackEnd.Extractores import Extractor_XML
from BackEnd.Extractores import Extractor_CSV
from BackEnd.utils.SQL import SQL

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

api = Api(app)

# Execute for SSL Certificate creation in same folder as carga.py
# openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Swagger UI configuration
SWAGGER_URL = '/swagger-ui'
API_URL = '/static/swagger.json'  # Path to the Swagger JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Carga API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Serve the swagger.json file
@app.route('/static/swagger.json')
def swagger_json():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'swagger.json')

# Read the API key from an environment variable
API_KEY = os.getenv('API_KEY', 'dev-key-1234')  # Valor por defecto para desarrollo

# Authentication decorator
def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.args.get('api_key')
        logging.debug(f"API Key received: {key}")
        if key and key == API_KEY:
            return func(*args, **kwargs)
        else:
            logging.warning("Unauthorized API Key.")
            return {"error": "Unauthorized"}, 401  # Return a dictionary directly
    return wrapper

class LoadData(Resource):
    def post(self):
        try:
            logging.debug("Initializing the database...")
            sql_instance = SQL()
            sql_instance.initialize_db()

            logging.debug("Retrieving extractor type from the request...")
            extractor_type = request.args.get('type')
            logging.debug(f"Extractor type received: {extractor_type}")

            if extractor_type == 'csv':
                data = Extractor_CSV.get_datos()
            elif extractor_type == 'json':
                data = Extractor_JSON.get_datos()
            elif extractor_type == 'xml':
                data = Extractor_XML.get_datos()
            else:
                logging.error("Invalid extractor type.")
                return {"error": "Invalid extractor type"}, 400

            logging.debug(f"Data extracted: {data}")

            # Ensure the data is JSON serializable
            if not isinstance(data, (list, dict)):
                logging.error("Extracted data is not JSON serializable.")
                return {"error": "Extracted data is not JSON serializable"}, 500

            logging.debug("Loading data into the database...")
            sql_instance.cargar_datos(data)

            logging.info("Data successfully loaded into the database.")
            return {"message": "Database initialized and data loaded successfully"}, 200

        except Exception as e:
            logging.error(f"An unexpected error occurred: {str(e)}")
            return {"error": f"An error occurred: {e}"}, 500

# Add the resources to the API
api.add_resource(LoadData, '/load')

# Run the app
if __name__ == '__main__':
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')
    print(f"Certificados en: {cert_path} y {key_path}")
    print(f"Certificados existen: {os.path.exists(cert_path)} y {os.path.exists(key_path)}")
    print("\n=== Rutas de acceso disponibles ===")
    print("Swagger UI: https://localhost:8000/swagger-ui")
    print("API Endpoint: https://localhost:8000/load")
    print("Documentación JSON: https://localhost:8000/static/swagger.json")
    print("================================\n")
    app.run(ssl_context=(cert_path, key_path), debug=True, host='0.0.0.0', port=8000)