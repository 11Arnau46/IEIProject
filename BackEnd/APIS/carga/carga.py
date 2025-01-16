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

    def _generate_general_report(self, sources):
        """
        Genera un informe general combinando las estadísticas de múltiples fuentes.
        """
        total_stats = {
            'processed': 0,
            'loaded': 0,
            'rejected': 0,
            'repaired': 0,
            'details': {
                'rechazados': [],
                'reparados': []
            }
        }

        for source in sources:
            if source not in ["xml", "json", "csv"]:
                continue

            # Procesar estadísticas
            stats_path = root_dir / 'Resultados' / f'log-{source}' / f'log-estadisticas-{source}.log'
            stats_content = self._read_log_file(stats_path)
            if stats_content:
                for line in stats_content.split('\n'):
                    if "Total de datos procesados:" in line:
                        total_stats['processed'] += int(line.split(':')[1].strip())
                    elif "Total de registros cargados correctamente:" in line:
                        total_stats['loaded'] += int(line.split(':')[1].strip())
                    elif "Total de registros rechazados:" in line:
                        total_stats['rejected'] += int(line.split(':')[1].strip())
                    elif "Total de registros reparados:" in line:
                        total_stats['repaired'] += int(line.split(':')[1].strip())

            # Procesar rechazados
            rejected_path = root_dir / 'Resultados' / f'log-{source}' / f'log-rechazados-{source}.log'
            rejected_content = self._read_log_file(rejected_path)
            if rejected_content:
                total_stats['details']['rechazados'].extend(
                    [line for line in rejected_content.split('\n') if line.strip()]
                )

            # Procesar reparados
            repaired_path = root_dir / 'Resultados' / f'log-{source}' / f'log-reparados-{source}.log'
            repaired_content = self._read_log_file(repaired_path)
            if repaired_content:
                total_stats['details']['reparados'].extend(
                    [line for line in repaired_content.split('\n') if line.strip()]
                )

        return total_stats

    @require_api_key
    def get(self, wrapper, tipo=None):
        """
        Obtiene el contenido del archivo de log según el tipo especificado y el wrapper.
        """
        if wrapper == "general":
            sources = request.args.get('sources', '').split(',')
            if not sources or '' in sources:
                return {"error": "Debe especificar las fuentes de datos (sources=csv,json,xml)"}, 400

            # Generar informe general
            report = self._generate_general_report(sources)
            
            if tipo == "estadisticas":
                response_text = "--------------------------------------------------------------------------------\n"
                response_text += "ESTADÍSTICAS GENERALES (fuente = COMBINADO)\n"
                response_text += "--------------------------------------------------------------------------------\n"
                response_text += f"Total de datos procesados: {report['processed']}\n"
                response_text += f"Total de registros cargados correctamente: {report['loaded']}\n"
                response_text += f"Total de registros rechazados: {report['rejected']}\n"
                response_text += f"Total de registros reparados: {report['repaired']}\n"
                response_text += "--------------------------------------------------------------------------------\n"
                return Response(response_text, mimetype='text/plain')
            elif tipo == "rechazados":
                response_text = "Registros con errores y rechazados:\n"
                response_text += "{Fuente de datos, nombre, Localidad, motivo del error}\n"
                response_text += "\n".join(report['details']['rechazados'])
                return Response(response_text, mimetype='text/plain')
            elif tipo == "reparados":
                response_text = "Registros con errores y reparados:\n"
                response_text += "{Fuente de datos, nombre, Localidad, motivo del error, operación realizada}\n"
                response_text += "\n".join(report['details']['reparados'])
                return Response(response_text, mimetype='text/plain')
            else:
                return jsonify(report)

        if tipo not in ["estadisticas", "rechazados", "reparados"]:
            return {"error": "Tipo de log no válido"}, 400
            
        if wrapper not in ["xml", "json", "csv", "general"]:
            return {"error": "Tipo de wrapper no válido"}, 400

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