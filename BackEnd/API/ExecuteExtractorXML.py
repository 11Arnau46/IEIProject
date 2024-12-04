import os
import subprocess

from flasgger import swag_from
from flask_restful import Resource

class ExecuteExtractorXML(Resource):
    @swag_from('docs/execute_xml.yml')
    def post(self):
        #print the current working directory here
        print("Current working directory:", os.getcwd())

        subprocess.run(["python3", "BackEnd/Extractor_XML.py"])
        return {"message": "Extractor_XML executed successfully"}, 200