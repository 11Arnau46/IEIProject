import logging
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_restful import Api, Resource
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Define the root project directory
root_dir = Path(__file__).resolve().parents[3]
sys.path.append(str(root_dir))

from BackEnd.Extractores import Extractor_JSON
from BackEnd.Extractores import Extractor_XML
from BackEnd.Extractores import Extractor_CSV
from BackEnd.Extractores import ExtractorXML
from BackEnd.utils.SQL import SQL

app = Flask(__name__)
# Configurar CORS para permitir todas las rutas y orígenes
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

api = Api(app)

# Read the API key from .env file
API_KEY = os.getenv('API_KEY', 'FUpP6o1K026VbhSuRBF0ehkKjqc5pztig_tTpn1tBeY')

# Authentication decorator
def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.args.get('api_key')
        logging.debug(f"API Key received: {key}")
        if key and key == API_KEY:
            return func(*args, **kwargs)
        else:
            logging.warning("Unauthorized API Key.")
            return jsonify({"error": "Unauthorized"}), 401
    return wrapper

class LoadData(Resource):
    @require_api_key
    def post(self):
        try:
            logging.debug("Initializing the database...")
            sql_instance = SQL()
            sql_instance.initialize_db()

            logging.debug("Retrieving extractor types from the request...")
            extractor_types = request.args.get('types')
            if not extractor_types:
                logging.error("No extractor types provided.")
                return {"error": "No extractor types provided"}, 400

            extractor_types = extractor_types.split(',')
            logging.debug(f"Extractor types received: {extractor_types}")

            for extractor_type in extractor_types:
                logging.debug(f"Processing extractor type: {extractor_type}")
                data = None
                
                if extractor_type == 'csv':
                    data = Extractor_CSV.get_datos()
                elif extractor_type == 'json':
                    data = Extractor_JSON.get_datos()
                elif extractor_type == 'xml':
                    ExtractorXML.process_json()
                    data = ExtractorXML.get_datos()
                else:
                    logging.error(f"Invalid extractor type: {extractor_type}")
                    return {"error": f"Invalid extractor type: {extractor_type}"}, 400

                if data is None:
                    error_msg = f"No se pudieron obtener datos del extractor {extractor_type}. Verifica que el servicio {extractor_type} esté funcionando."
                    logging.error(error_msg)
                    return {"error": error_msg}, 500

                logging.debug(f"Data extracted for {extractor_type}: {data}")
                sql_instance.cargar_datos(data)

            logging.info("Data successfully loaded into the database.")
            return {"message": "Database initialized and data loaded successfully"}, 200
        except Exception as e:
            error_msg = f"An error occurred while processing {extractor_type if 'extractor_type' in locals() else 'unknown'} data: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}, 500

class WrapperLog(Resource):
    """
    WrapperLog es un recurso Flask-RESTful que maneja la obtención y eliminación de archivos de log.
    """
    
    def _read_log_file(self, log_file_path):
        """
        Lee un archivo de log con diferentes codificaciones y maneja los errores apropiadamente.
        """
        # Lista de codificaciones a intentar
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(log_file_path, 'r', encoding=encoding) as log_file:
                    return log_file.read()
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                return None
            except Exception as e:
                return None
        
        return None

    @require_api_key
    def get(self, wrapper, tipo=None):
        """
        Obtiene el contenido del archivo de log según el tipo especificado y el wrapper.
        """
        if tipo not in ["estadisticas", "rechazados", "reparados"]:
            return {"error": "Tipo de log no válido"}, 400
            
        if wrapper not in ["xml", "json", "csv", "general"]:
            return {"error": "Tipo de wrapper no válido"}, 400

        if wrapper == "general":
            # Obtener las fuentes de datos de los parámetros de la consulta
            sources = request.args.get('sources', '').split(',')
            if not sources or '' in sources:
                return {"error": "Debe especificar las fuentes de datos (sources=csv,json,xml)"}, 400

            combined_content = ""
            total_processed = 0
            total_loaded = 0
            total_rejected = 0
            total_repaired = 0
            if tipo == "estadisticas":
                combined_content = "--------------------------------------------------------------------------------\n"
                combined_content += "ESTADÍSTICAS GENERALES (fuente = COMBINADO)\n"
                combined_content += "--------------------------------------------------------------------------------\n"
            elif tipo == "reparados":
                combined_content = "Registros con errores y reparados:\n"
                combined_content += "{Fuente de datos, nombre, Localidad, motivo del error, operación realizada}\n"
            elif tipo == "rechazados":
                combined_content = "Registros con errores y rechazados:\n"
                combined_content += "{Fuente de datos, nombre, Localidad, motivo del error}\n"
            for source in sources:
                if source not in ["xml", "json", "csv"]:
                    continue
                
                log_file_path = root_dir / 'Resultados' / f'log-{source}' / f'log-{tipo}-{source}.log'
                content = self._read_log_file(log_file_path)
                
                if content:
                    if tipo == "estadisticas":
                        # Extraer números de las estadísticas
                        for line in content.split('\n'):
                            if "Total de datos procesados:" in line:
                                total_processed += int(line.split(':')[1].strip())
                            elif "Total de registros cargados correctamente:" in line:
                                total_loaded += int(line.split(':')[1].strip())
                            elif "Total de registros rechazados:" in line:
                                total_rejected += int(line.split(':')[1].strip())
                            elif "Total de registros reparados:" in line:
                                total_repaired += int(line.split(':')[1].strip())
                    else:
                        # Para rechazados y reparados, añadir el contenido con un único salto de línea entre fuentes
                        if content.strip():  # Solo añadir contenido si no está vacío
                            if combined_content.endswith('\n'):
                                combined_content += content.strip()
                            else:
                                combined_content += '\n' + content.strip()
            if tipo == "estadisticas":
                combined_content += f"Total de datos procesados: {total_processed}\n"
                combined_content += f"Total de registros cargados correctamente: {total_loaded}\n"
                combined_content += f"Total de registros rechazados: {total_rejected}\n"
                combined_content += f"Total de registros reparados: {total_repaired}\n"
                combined_content += "--------------------------------------------------------------------------------\n"
            return Response(combined_content, mimetype='text/plain', status='200')
        
        # Código original para logs individuales
        log_file_path = root_dir / 'Resultados' / f'log-{wrapper}' / f'log-{tipo}-{wrapper}.log'
        content = self._read_log_file(log_file_path)

        if content is None:
            return {"error": f"Log de {tipo} no encontrado"}, 404
            
        return Response(content, mimetype='text/plain', status='200')

    @require_api_key
    def delete(self, wrapper, tipo=None):
        """
        Elimina el archivo de log según el tipo especificado y el wrapper.
        """
        if wrapper not in ["xml", "json", "csv"]:
            return {"error": "Tipo de wrapper no válido"}, 400

        # Cerrar los handlers antes de eliminar
        for log_type in ["estadisticas", "rechazados", "reparados"]:
            logger_name = f'{log_type}_{wrapper.upper()}'
            if logger_name in logging.root.manager.loggerDict:
                logger = logging.getLogger(logger_name)
                for handler in logger.handlers[:]:
                    handler.close()
                    logger.removeHandler(handler)

        if tipo:
            if tipo not in ["estadisticas", "rechazados", "reparados"]:
                return {"error": "Tipo de log no válido"}, 400
                
            log_file_path = root_dir / 'Resultados' / f'log-{wrapper}' / f'log-{tipo}-{wrapper}.log'
            try:
                if log_file_path.exists():
                    os.remove(log_file_path)
                return {"message": f"Log de {tipo} eliminado exitosamente"}
            except Exception as e:
                return {"error": f"Error al eliminar el log de {tipo}: {e}"}, 500
        else:
            # Eliminar todos los logs del wrapper
            try:
                for log_type in ["estadisticas", "rechazados", "reparados"]:
                    path = root_dir / 'Resultados' / f'log-{wrapper}' / f'log-{log_type}-{wrapper}.log'
                    if path.exists():
                        os.remove(path)
                return {"message": "Todos los archivos de log han sido eliminados exitosamente"}
            except Exception as e:
                return {"error": f"Error al eliminar los archivos de log: {e}"}, 500

# Swagger UI configuration
SWAGGER_URL = '/swagger-ui'
API_URL = '/static/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Carga API"
    }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Serve the swagger.json file
@app.route('/static/swagger.json')
def swagger_json():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'swagger.json')

# Add the resources to the API
api.add_resource(LoadData, '/load')
api.add_resource(WrapperLog, 
                '/log/<string:wrapper>/<string:tipo>',
                '/log/<string:wrapper>')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cert_path = os.path.join(os.path.dirname(__file__), 'cert.pem')
    key_path = os.path.join(os.path.dirname(__file__), 'key.pem')
    print(f"Certificados en: {cert_path} y {key_path}")
    print(f"Certificados existen: {os.path.exists(cert_path)} y {os.path.exists(key_path)}")
    print("\n=== Rutas de acceso disponibles ===")
    print("Swagger UI: https://localhost:8000/swagger-ui")
    print("API Endpoint: https://localhost:8000/load")
    print("Documentación JSON: https://localhost:8000/static/swagger.json")
    print("\nEndpoints de carga de datos:")
    print("  → GET    https://localhost:8000/load/?types=csv,json,xml&api_key=")
    print("\nEndpoints de gestión de logs:")
    print("  → GET    https://localhost:8000/log/{formato}/{tipo}")
    print("           formatos: csv, json, xml, general")
    print("           tipos: reparados, rechazados, estadisticas")
    print("           Para el formato general, añadir ?sources=csv,json,xml")
    print("  → DELETE https://localhost:8000/log/{formato}/{tipo}")
    print("  → DELETE https://localhost:8000/log/{formato}")
    print("================================\n")
    app.run(ssl_context=(cert_path, key_path), debug=True, host='0.0.0.0', port=8000)