import pandas as pd
import json
import re
from Location_Finder import LocationFinder


# Función para parsear y preservar todas las claves, incluyendo duplicados
def parse_json_with_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Utilizamos object_pairs_hook para conservar el orden y los duplicados
        data = json.load(file, object_pairs_hook=lambda pairs: pairs)
    return data

# Función para limpiar coordenadas
def clean_coordinates(value):
    if value is not None and isinstance(value, str):
        # Mantener solo números, puntos y guiones
        return re.sub(r'[^0-9\.\-]', '', value)
    return value

# Ruta al archivo JSON
json_path = '../Fuentes_de_datos/Demo/eus.json'

# Cargar los datos preservando los campos duplicados
json_data = parse_json_with_duplicates(json_path)

# Diccionario para almacenar los datos extraídos
data = {
    'nomMonumento': [],
    'tipoMonumento': [],
    'direccion': [],
    'codigo_postal': [],
    'longitud': [],
    'latitud': [],
    'descripcion': [],
    'codLocalidad': [],
    'nomLocalidad': [],
    'codProvincia': [],
    'nomProvincia': []
}

# Conjunto para realizar un seguimiento de los monumentos ya procesados
seen_monuments = set()

# Función para clasificar el tipo de monumento
def get_tipo_monumento(denominacion):
    if not isinstance(denominacion, str):
        return pd.NA
        
    denominacion_lower = denominacion.lower()
    palabras_clave = {
        "YacimientoArqueologico": ["yacimiento arqueológico", "Yacimiento Arqueológico"],
        "MonasterioConvento": ["monasterio", "convento", "Monasterio", "Convento"],
        "IglesiaErmita": ["iglesia", "ermita", "catedral", "basílica", 
                          "Iglesia", "Ermita", "Catedral", "Basílica"],
        "CastilloTorreFuerte": ["castillo", "torre", "fuerte",
                                "Castillo", "Torre", "Fuerte"],
        "EdificioPalacio": ["edificio", "palacio", "Edificio", "Palacio"],
        "Puente": ["puente", "Puente"],
        "Otros": ["santuario", "teatro", "plaza", "paseo", "casco", 
                  "villa", "ferrería", "mercado", "fábrica",
                  "Santuario", "Teatro", "Plaza", "Paseo", "Casco", 
                  "Villa", "Ferrería", "Mercado", "Fábrica"]
    }
    
    for tipo, keywords in palabras_clave.items():
        if any(keyword in denominacion for keyword in keywords):
            return tipo
    return "Otros monumentos"

def limpiar_campo_duplicado(valor):
    if not isinstance(valor, str):
        return valor
    # Divide el string por espacios y elimina duplicados manteniendo el orden
    partes = valor.split()
    partes_unicas = []
    for parte in partes:
        if parte not in partes_unicas:
            partes_unicas.append(parte)
    return ' '.join(partes_unicas)

# Extraer información de cada elemento del JSON
for monumento in json_data:
    # Convertir la lista de tuplas a un diccionario para campos únicos
    monumento_dict = {}
    # Lista para almacenar todas las direcciones
    address_list = []
    
    for key, value in monumento:
        if key == 'address':
            if isinstance(value, str):
                address_list.append(value)
        else:
            monumento_dict[key] = value
    
    nomMonumento = monumento_dict.get('documentName', pd.NA)
    
    # Verificar si el monumento ya ha sido procesado
    if nomMonumento in seen_monuments:
        continue  # Si ya se procesó, omitir este monumento
    
    tipoMonumento = get_tipo_monumento(nomMonumento) if nomMonumento is not pd.NA else pd.NA
    
    # Obtener la primera dirección que no esté vacía
    direccion = next((addr for addr in address_list if addr.strip()), pd.NA)
    
    codigo_postal = monumento_dict.get('postalCode', pd.NA)
    
    # Obtener coordenadas
    latlong = monumento_dict.get('latitudelongitude', '').split(',')
    if len(latlong) == 2:
        latitud = clean_coordinates(latlong[0])  # Limpiar latitud
        longitud = clean_coordinates(latlong[1])  # Limpiar longitud
    else:
        latitud = clean_coordinates(monumento_dict.get('latwgs84', pd.NA))
        longitud = clean_coordinates(monumento_dict.get('lonwgs84', pd.NA))
    
    descripcion = monumento_dict.get('documentDescription', pd.NA)
    
    codLocalidad = limpiar_campo_duplicado(monumento_dict.get('municipalitycode', pd.NA))
    nomLocalidad = limpiar_campo_duplicado(monumento_dict.get('municipality', pd.NA))
    
    codProvincia = limpiar_campo_duplicado(monumento_dict.get('territorycode', pd.NA))
    nomProvincia = limpiar_campo_duplicado(monumento_dict.get('territory', pd.NA))

    # Añadir los datos al diccionario
    data['nomMonumento'].append(nomMonumento)
    data['tipoMonumento'].append(tipoMonumento)
    data['direccion'].append(direccion)
    data['codigo_postal'].append(codigo_postal)
    data['latitud'].append(latitud)
    data['longitud'].append(longitud)
    data['descripcion'].append(descripcion)
    data['codLocalidad'].append(codLocalidad)
    data['nomLocalidad'].append(nomLocalidad)
    data['codProvincia'].append(codProvincia)
    data['nomProvincia'].append(nomProvincia)

    # Agregar el nombre del monumento al conjunto de monumentos procesados
    seen_monuments.add(nomMonumento)

# Crear un DataFrame con los datos extraídos
df_result = pd.DataFrame(data)

# Separar los datos en dos DataFrames
df_con_coords = pd.DataFrame([{k: v[i] for k, v in data.items()} 
                            for i in range(len(data['nomMonumento'])) 
                            if pd.notna(data['longitud'][i]) and pd.notna(data['latitud'][i])])

df_sin_coords = pd.DataFrame([{k: v[i] for k, v in data.items()} 
                            for i in range(len(data['nomMonumento'])) 
                            if pd.isna(data['longitud'][i]) or pd.isna(data['latitud'][i])])

# Mostrar información sobre los datos separados
print(f"Monumentos con coordenadas: {len(df_con_coords)}")
print(f"Monumentos sin coordenadas: {len(df_sin_coords)}")

# Guardar los datos en formato JSON
df_con_coords.to_json(
    '../Resultados/JSONtoJSON_con_coords.json',
    orient='records',
    force_ascii=False,
    indent=4,
    default_handler=str
)
if len(df_sin_coords) > 0:
    df_sin_coords.to_json(
        '../Resultados/JSONtoJSON_sin_coords.json',
        orient='records',
        force_ascii=False,
        indent=4,
        default_handler=str
    )


json_path = '../Resultados/JSONtoJSON_Corregido.json'
location_finder = LocationFinder(json_path)
# Procesar el JSON y guardar los resultados en el mismo archivo con código postal y direcciones completas
results = location_finder.process_json()
location_finder.save_results_to_json(results)
print(f"Archivo final guardado en {json_path}.")