from flask import Flask
from flasgger import Swagger
from flask_restful import Api
from BackEnd.API.ExecuteExtractorCSV import ExecuteExtractorCSV
from BackEnd.API.ExecuteExtractorJSON import ExecuteExtractorJSON
from BackEnd.API.ExecuteExtractorXML import ExecuteExtractorXML
#from GetDataFromDB import GetDataFromDB
#from LoadDataToDB import LoadDataToDB

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)


api.add_resource(ExecuteExtractorCSV, '/execute_csv')
api.add_resource(ExecuteExtractorJSON, '/execute_json')
api.add_resource(ExecuteExtractorXML, '/execute_xml')
#api.add_resource(GetDataFromDB, '/get_data')
#api.add_resource(LoadDataToDB, '/load_data')

# http://127.0.0.1:5000/apidocs/
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1' , port=5000)