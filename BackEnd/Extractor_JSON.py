import pandas as pd
import json

# Función para parsear y preservar todas las claves, incluyendo duplicados
def parse_json_with_duplicates(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        # Utilizamos object_pairs_hook para conservar el orden y los duplicados
        data = json.load(file, object_pairs_hook=lambda pairs: pairs)
    return data

# Ruta al archivo JSON
json_path = '../Fuentes_de_datos/Euskadi/eus.json'

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

# Función para clasificar el tipo de monumento
def get_tipo_monumento(denominacion):
    if not isinstance(denominacion, str):
        return pd.NA
        
    denominacion_lower = denominacion.lower()
    palabras_clave = {
        "Yacimiento arqueológico": ["yacimiento arqueológico", "Yacimiento Arqueológico"],
        "Monasterio-Convento": ["monasterio", "convento", "Monasterio", "Convento"],
        "Iglesia-Ermita": ["iglesia", "ermita", "catedral", "basílica", 
                        "Iglesia", "Ermita", "Catedral", "Basílica"],
        "Castillo-Torre-Fuerte": ["castillo", "torre", "fuerte",
                                "Castillo", "Torre", "Fuerte"],
        "Edificio-Palacio": ["edificio", "palacio", "Edificio", "Palacio"],
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
    tipoMonumento = get_tipo_monumento(nomMonumento) if nomMonumento is not pd.NA else pd.NA
    
    # Obtener la primera dirección que no esté vacía
    direccion = next((addr for addr in address_list if addr.strip()), pd.NA)
    
    codigo_postal = monumento_dict.get('postalCode', pd.NA)
    
    # Obtener coordenadas
    latlong = monumento_dict.get('latitudelongitude', '').split(',')
    if len(latlong) == 2:
        latitud = latlong[0]
        longitud = latlong[1]
    else:
        latitud = monumento_dict.get('latwgs84', pd.NA)
        longitud = monumento_dict.get('lonwgs84', pd.NA)
    
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

# Crear un DataFrame con los datos extraídos
df_result = pd.DataFrame(data)

# Mostrar el DataFrame resultante
print(df_result.head())

# Guardar los datos en formato JSON
df_result.to_json(
    '../Resultados/JSONtoJSON.json',
    orient='records',
    force_ascii=False,
    indent=4,
    default_handler=str
)