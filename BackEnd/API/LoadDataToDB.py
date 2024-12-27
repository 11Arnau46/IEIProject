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
            with open(log_file_path, 'r', encoding='utf-8') as log_file:  # Change encoding if needed
                logs = log_file.read()
            return Response(logs, mimetype='text/plain; charset=utf-8')  # Set charset explicitly
        except FileNotFoundError:
            return {"error": "Log file not found"}, 404
        except UnicodeDecodeError as e:
            return {"error": f"Encoding issue: {e}"}, 500
