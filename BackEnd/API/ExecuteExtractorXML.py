import os
import subprocess
from flask_restful import Resource
from flask import Response
from pathlib import Path

class ExecuteExtractorXML(Resource):
    def post(self):
        # Define the relative path to main.py
        main_py_path = Path(__file__).resolve().parents[2] / 'main.py'
        
        # Print the path to main.py for debugging purposes
        print("Path to main.py:", main_py_path)
        
        # Determine the Python command to use
        python_command = "python3" if subprocess.run(["which", "python3"], capture_output=True).returncode == 0 else "py"
        
        # Print the Python command for debugging purposes
        print("Python command:", python_command)
        
        # Execute the command
        try:
            subprocess.run([python_command, main_py_path, "xml"], check=True)
        except subprocess.CalledProcessError as e:
            return {"error": f"Subprocess failed with error: {e}"}, 500
        
        # Define the path to the output file
        output_file_path = main_py_path.parent / 'Resultados' / 'XMLtoJSON_con_coords.json'
        
        # Print the path to the output file for debugging purposes
        print("Path to output file:", output_file_path)
        
        # Read the output file and return its contents
        try:
            with open(output_file_path, 'r') as output_file:
                output_data = output_file.read()
            return Response(output_data, mimetype='application/json')
        except FileNotFoundError:
            return {"error": "Output file not found"}, 404
        except Exception as e:
            return {"error": f"An error occurred while reading the output file: {e}"}, 500