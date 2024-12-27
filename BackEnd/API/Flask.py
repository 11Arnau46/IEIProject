from flask import Flask, jsonify
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from ExecuteExtractorCSV import ExecuteExtractorCSV
from ExecuteExtractorJSON import ExecuteExtractorJSON
from ExecuteExtractorXML import ExecuteExtractorXML
from LoadDataToDB import LoadDataToDB

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

# http://localhost:8080/swagger-ui/
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8080)