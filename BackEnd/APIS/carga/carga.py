from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os

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
#https://localhost:5000/swagger-ui?api_key=FUpP6o1K026VbhSuRBF0ehkKjqc5pztig_tTpn1tBeY

# Authentication decorator
def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.args.get('api_key')
        if key and key == API_KEY:
            return func(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return wrapper

class CargaExecute(Resource):
    @require_api_key
    def post(self):
        # Implement the logic to execute the data load
        return jsonify({"message": "Data load successful"})

    @require_api_key
    def get(self):
        # Implement the logic to get the load results
        return jsonify({"log-summary": "Load results fetched successfully"})

    @require_api_key
    def put(self):
        # Implement the logic to clear the load results
        return jsonify({"message": "Load results cleared successfully"})

class CargaLog(Resource):
    @require_api_key
    def get(self):
        # Implement the logic to get the log file content
        return jsonify({"log": "Log file content here..."})

    @require_api_key
    def delete(self):
        # Implement the logic to clear the log file content
        return jsonify({"message": "Log file content cleared successfully"})

# Add the resources to the API
api.add_resource(CargaExecute, '/carga')
api.add_resource(CargaLog, '/carga/log')


# https://0.0.0.0:5000/swagger-ui/?api_key=FUpP6o1K026VbhSuRBF0ehkKjqc5pztig_tTpn1tBeY#/
if __name__ == '__main__':
    app.run(ssl_context=('cert.pem', 'key.pem'), debug=True, host='0.0.0,0', port=5000)