import sys
from pathlib import Path

# Define the root project directory and add it to Python path
root_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(root_dir))

from flask import Flask, jsonify, request, send_from_directory, Response
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import subprocess
import os
from BackEnd.utils.Otros import data_source
from BackEnd.Wrappers.Wrapper_CSV import process_csv

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
        'app_name': "WrapperCSV API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

class WrapperCSVExecute(Resource):
    """
    WrapperCSVExecute is a Flask-RESTful resource that handles the execution of a data transformation script to CSV.
    """

    def post(self):
        """
        Executes the main.py script with the 'csv' argument using python3 or py command.
        """
        # Execute wrapper_CSV.py
        process_csv()
        
        # Define the path to the output file
        output_file_path = root_dir / 'Resultados' / 'CSVtoJSON_con_coords.json'
        
        # Print the path to the output file for debugging purposes
        print("Path to output file:", output_file_path)
        
        # Read the output file and return its contents
        try:
            with open(output_file_path, 'r', encoding='utf-8') as output_file:
                output_data = output_file.read()
            return Response(output_data, mimetype='application/json', status=201)
        except FileNotFoundError:
            return {"error": "Output file not found"}, 404
        except Exception as e:
            return {"error": f"An error occurred while reading the output file: {e}"}, 500

    def delete(self):
        """
        Deletes the output CSV file generated by the data transformation script.
        """
        output_file_path = root_dir / 'Resultados' / 'CSVtoJSON_con_coords.json'
        try:
            os.remove(output_file_path)
            return {"message": "Output file deleted successfully"}
        except FileNotFoundError:
            return {"error": "Output file not found"}, 404
        except Exception as e:
            return {"error": f"An error occurred while deleting the output file: {e}"}, 500

# Add the resources to the API
api.add_resource(WrapperCSVExecute, '/wrapperCSV/execute')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("API WrapperCSV iniciada exitosamente!")
    print("="*50)
    print("\nDocumentación disponible en:")
    print("  → http://localhost:8083/swagger-ui")
    print("\nEndpoints disponibles:")
    print("  → POST   http://localhost:8083/wrapperCSV/execute")
    print("\nPresiona Ctrl+C para detener el servidor")
    print("="*50 + "\n")
    app.run(debug=True, host='localhost', port=8083)