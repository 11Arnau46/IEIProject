import os
import subprocess
from flask_restful import Resource
from flasgger import swag_from

class ExecuteExtractorJSON(Resource):
    @swag_from('docs/execute_json.yml')
    def post(self):
        #print the current working directory here
        print("Current working directory:", os.getcwd())

        subprocess.run(["python3", "BackEnd/Extractor_JSON.py"])
        return {"message": "Extractor_JSON executed successfully"}, 200