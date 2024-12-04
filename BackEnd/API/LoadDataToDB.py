from flask_restful import Resource
from SQL.BDConnection import BDConnection
from SQL.Json_Loader import cargar_datos

class LoadDataToDB(Resource):
    def post(self):
        bd_connection = BDConnection()
        engine_with_db = bd_connection.init_db()
        if engine_with_db is None:
            return {"message": "Error initializing the database"}, 500
        session = bd_connection.session
        try:
            cargar_datos(session, "path_to_your_json_file.json")
            return {"message": "Data loaded successfully"}, 200
        except Exception as e:
            return {"message": f"Error loading data: {e}"}, 500
        finally:
            bd_connection.close()