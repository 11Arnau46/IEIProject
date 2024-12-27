import os
import sys
from pathlib import Path
from flask import Flask, jsonify, request
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint

# Ensure the BackEnd directory is in the Python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from BackEnd.API.ExecuteExtractorCSV import ExecuteExtractorCSV
from BackEnd.API.ExecuteExtractorJSON import ExecuteExtractorJSON
from BackEnd.API.ExecuteExtractorXML import ExecuteExtractorXML
from BackEnd.API.LoadDataToDB import LoadDataToDB
from BackEnd.utils.Otros import get_total_records_added_correctly

app = Flask(__name__)
api = Api(app)

# Swagger UI configuration
SWAGGER_URL = '/swagger-ui'
API_URL = '/static/swagger.json'  # Path to the Swagger JSON file

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={  # Swagger UI config overrides
        'app_name': "IEIProject API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

api.add_resource(ExecuteExtractorCSV, '/extractor/execute_csv', endpoint='extractor_csv')
api.add_resource(ExecuteExtractorJSON, '/extractor/execute_json', endpoint='extractor_json')
api.add_resource(ExecuteExtractorXML, '/extractor/execute_xml', endpoint='extractor_xml')
api.add_resource(LoadDataToDB, '/load_results', endpoint='load_results')

# Get the root project directory
root_dir = Path(__file__).resolve().parents[2]


# Endpoint to clear necessary JSON and log files
@app.route('/clear_files', methods=['POST'])
def clear_files():
    files_to_clear = [
        root_dir / 'Resultados' / 'CSVtoJSON_Corregido.json',
        root_dir / 'Resultados' / 'JSONtoJSON_con_coords.json',
        root_dir / 'Resultados' / 'XMLtoJSON_con_coords.json',
        root_dir / 'Resultados' / 'XMLtoJSON_sin_coords.json',
        root_dir / 'Resultados' / 'log-summary.log'
    ]
    for file_path in files_to_clear:
        open(file_path, 'w').close()
    return jsonify({"message": "Files cleared successfully"})

# Endpoint to get the total correct loads
@app.route('/total_correct_loads', methods=['GET'])
def total_correct_loads():
    total_correct_loads = get_total_records_added_correctly()
    return jsonify({"total": total_correct_loads})

# http://localhost:8080/swagger-ui/
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)