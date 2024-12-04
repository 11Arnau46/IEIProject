import os
import subprocess

from flasgger import swag_from
from flask_restful import Resource

class ExecuteExtractorCSV(Resource):
    @swag_from('docs/execute_csv.yml')
    def post(self):
        #print the current working directory here
        print("Current working directory:", os.getcwd())
        subprocess.run(["python3", "BackEnd/Extractor_CSV.py"])
        return {"message": "Extractor_CSV executed successfully"}, 200