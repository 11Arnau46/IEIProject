from flask import jsonify
from flask_restful import Resource
from SQL.BDConnection import BDConnection

class GetDataFromDB(Resource):
    def get(self):
        bd_connection = BDConnection()
        session = bd_connection.session
        data = session.execute("SELECT * FROM monumentos").fetchall()
        bd_connection.close()
        return jsonify(data)