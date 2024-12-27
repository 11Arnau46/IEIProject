from flask_restful import Resource
from flask import Response
from pathlib import Path


# Get the root project directory
root_dir = Path(__file__).resolve().parents[2]

# Path to the log file
log_file_path = root_dir / 'Resultados' / 'log-summary.log'

class LoadDataToDB(Resource):
    def get(self):
        try:
            with open(log_file_path, 'r', encoding='latin-1') as log_file:
                logs = log_file.read()
            return Response(logs, mimetype='text/plain')
        except FileNotFoundError:
            return {"error": "Log file not found"}, 404