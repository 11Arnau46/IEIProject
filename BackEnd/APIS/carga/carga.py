from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os
import sys
from pathlib import Path

from BackEnd.Extractores import Extractor_JSON
from BackEnd.Extractores import Extractor_XML
from BackEnd.Extractores import Extractor_CSV

# Define the root project directory
root_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(root_dir))


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

# Read the API key from an environment variable
API_KEY = os.getenv('API_KEY')

# Authentication decorator
def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.args.get('api_key')
        if key and key == API_KEY:
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return wrapper

class LoadData(Resource):
    @require_api_key
    def post(self):
        try:
            SQL.initialize_db()

            # Get the extractor type from the request
            extractor_type = request.args.get('type')
            if extractor_type == 'csv':
                data = Extractor_CSV.get_datos()
                SQL.cargar_datos(self,data)
            elif extractor_type == 'json':
                data = Extractor_JSON.get_datos()
                SQL.cargar_datos(self,data)
            elif extractor_type == 'xml':
                data = Extractor_XML.get_datos()
                SQL.cargar_datos(self,data)
            else:
                return jsonify({"error": "Invalid extractor type"}), 400

            return jsonify({"message": "Database initialized and data loaded successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"An error occurred: {e}"}), 500

# Add the resources to the API
api.add_resource(LoadData, '/load')

# https://0.0.0.0:8000/swagger-ui/?api_key=FUpP6o1K026VbhSuRBF0ehkKjqc5pztig_tTpn1tBeY#/
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True, host='localhost', port=8000)