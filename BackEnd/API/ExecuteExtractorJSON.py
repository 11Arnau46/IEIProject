import os
import subprocess
from flask_restful import Resource
from flask import Response
from pathlib import Path

class ExecuteExtractorJSON(Resource):
    def post(self):
        # Define the relative path to main.py
        main_py_path = Path(__file__).resolve().parents[2] / 'main.py'
        
        # Print the path to main.py for debugging purposes
        print("Path to main.py:", main_py_path)
        
        # Execute the command with python3
        try:
            subprocess.run(["python3", main_py_path, "json"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"python3 failed with error: {e}, trying py command")
            try:
                subprocess.run(["py", main_py_path, "json"], check=True)
            except subprocess.CalledProcessError as e:
                return {"error": f"Subprocess failed with error: {e}"}, 500
        
        # Define the path to the output file
        output_file_path = main_py_path.parent / 'Resultados' / 'JSONtoJSON_con_coords.json'
        
        # Print the path to the output file for debugging purposes
        print("Path to output file:", output_file_path)
        
        # Read the output file and return its contents
        try:
            with open(output_file_path, 'r', encoding='utf-8') as output_file:
                output_data = output_file.read()
            return Response(output_data, mimetype='application/json')
        except FileNotFoundError:
            return {"error": "Output file not found"}, 404
        except Exception as e:
            return {"error": f"An error occurred while reading the output file: {e}"}, 500