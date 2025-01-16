import sys
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory, Response
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import logging
import subprocess
import os

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
        'app_name': "WrapperXML API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Define the root project directory
root_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(root_dir))

from BackEnd.Wrappers.Wrapper_XML import process_xml


class WrapperXMLExecute(Resource):
    """
    WrapperXMLExecute is a Flask-RESTful resource that handles the execution of a data transformation script to XML.

    Methods
    -------
    post():
        Executes the main.py script with the 'xml' argument and handles any subprocess errors.
    """

    def post(self):
        """
        Executes the main.py script with the 'xml' argument using python3 or py command.

        This method attempts to run the main.py script located in the root directory of the project with the 'xml' argument.
        If the python3 command fails, it tries to execute the script using the py command. If both commands fail, it returns
        an error response.

        Returns
        -------
        dict
            A dictionary containing an error message if the subprocess fails.
        int
            HTTP status code 500 if the subprocess fails.
        """
        # Execute wrapper_XML.py
        process_xml()

        # Define the path to the output file
        output_file_path = root_dir / 'Resultados' / 'XMLtoJSON_con_coords.json'
        
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
        Deletes the output XML file generated by the data transformation script.

        This method attempts to delete the output XML file located in the 'Resultados' directory. If the file is not found,
        it returns a 404 error response. If any other error occurs, it returns a 500 error response.

        Returns
        -------
        dict
            A dictionary containing a success message if the file is deleted successfully, or an error message if the file
            is not found or another error occurs.
        int
            HTTP status code 200 if the file is deleted successfully, 404 if the file is not found, or 500 if another error occurs.
        """
        output_file_path = root_dir / 'Resultados' / 'XMLtoJSON_con_coords.'
        try:
            os.remove(output_file_path)
            return {"message": "Output file deleted successfully"}
        except FileNotFoundError:
            return {"error": "Output file not found"}, 404
        except Exception as e:
            return {"error": f"An error occurred while deleting the output file: {e}"}, 500

class WrapperXMLLog(Resource):
    """
    WrapperXMLLog is a Flask-RESTful resource that handles the retrieval and deletion of log files.

    Methods
    -------
    get():
        Retrieves the log file content.
    delete():
        Clears the log file content.
    """

    #todo: delete all not just final
    def get(self):
        """
        Retrieves the log file content.

        This method attempts to read the log file located in the 'Resultados' directory and returns its content. If the file
        is not found, it returns a 404 error response. If any other error occurs, it returns a 500 error response.

        Returns
        -------
        Response
            A Flask Response object containing the log file content with a 'text/plain' MIME type.
        dict
            A dictionary containing an error message if the file is not found or another error occurs.
        int
            HTTP status code 200 if the file is read successfully, 404 if the file is not found, or 500 if another error occurs.
        """
        log_file_path = root_dir / 'Resultados' / 'log-xml' / 'log-estadisticas-xml.log'
        try:
            with open(log_file_path, 'r', encoding='latin-1') as log_file:
                log_data = log_file.read()
            return Response(log_data, mimetype='text/plain')
        except FileNotFoundError:
            return {"error": "Log file not found"}, 404
        except Exception as e:
            return {"error": f"An error occurred while reading the log file: {e}"}, 500

    def delete(self):
        """
        Clears the log file content.

        This method attempts to clear the content of the log file located in the 'Resultados' directory. If any error occurs,
        it returns a 500 error response.

        Returns
        -------
        dict
            A dictionary containing a success message if the file is cleared successfully, or an error message if another error occurs.
        int
            HTTP status code 200 if the file is cleared successfully, or 500 if another error occurs.
        """
        log_file_path = root_dir / 'Resultados' / 'log-xml' / 'log-estadisticas-xml.log'
        try:
            open(log_file_path, 'w').close()
            return {"message": "Log file cleared successfully"}
        except Exception as e:
            return {"error": f"An error occurred while clearing the log file: {e}"}, 500

# Add the resources to the API
api.add_resource(WrapperXMLExecute, '/wrapperXML/execute')
api.add_resource(WrapperXMLLog, '/wrapperXML/log')

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port= 8081)