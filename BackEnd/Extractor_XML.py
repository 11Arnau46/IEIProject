import xml.etree.ElementTree as ET
import pandas as pd
import html
import re

# Path to the XML file
xml_path = '../Fuentes_de_datos/Castilla_i_leon/cle.xml'

# Parse the XML file
tree = ET.parse(xml_path)
root = tree.getroot()

# Diccionario para almacenar los datos extraídos
data = {
    'nombre': [],
    'tipoMonumento': [],
    'clasificacion': [],
    'tipoConstruccion': [],
    'codigo_postal': [],
    'descripcion': [],
    'periodoHistorico': [],
    'latitud': [],
    'longitud': [],
    'web': [],
    'localidad': [],
    'provincia': [],
    'municipio': []
}

# Function to classify the type of monument based on its name
def get_tipo_monumento(denominacion):
    denominacion = denominacion.lower()
    if "yacimiento" in denominacion:
        return "Yacimiento arqueológico"
    elif "monasterio" in denominacion or "convento" in denominacion:
        return "Monasterio-Convento"
    elif "iglesia" in denominacion or "ermita" in denominacion or "catedral" in denominacion or "basílica" in denominacion:
        return "Iglesia-Ermita"
    elif "castillo" in denominacion or "fortaleza" in denominacion or "torre" in denominacion:
        return "Castillo-Fortaleza-Torre"
    elif "jardín" in denominacion or "palacio" in denominacion:
        return "Edificio Singular"
    elif "puente" in denominacion:
        return "Puente"
    else:
        return "Otros"

# Function to remove HTML tags and clean text
def clean_text(text):
    # Decode HTML entities
    text = html.unescape(text)
    # Remove HTML tags
    text = re.sub(r'<[^>]*>', '', text)
    # Remove or replace newline characters
    text = text.replace('\n', ' ').replace('\r', ' ').strip()
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text

# Process each <monumento> in the XML
for monumento in root.findall('monumento'):
    # Safely extract text or set to null if missing
    nombre = monumento.findtext('nombre', default=None)
    tipo_monumento = get_tipo_monumento(nombre) if nombre else None
    clasificacion = monumento.findtext('clasificacion', default=None)
    tipo_construccion = monumento.findtext('tipoConstruccion', default=None)
    codigo_postal = monumento.findtext('codigoPostal', default=None)

    # Process and clean 'descripcion'
    descripcion_raw = monumento.findtext('Descripcion', default=None)
    descripcion = clean_text(descripcion_raw) if descripcion_raw else None

    # Extract multiple <periodoHistorico> as a comma-separated string
    periodo_historico_elements = monumento.findall('periodoHistorico')
    periodo_historico = ', '.join([ph.text for ph in periodo_historico_elements if ph.text]) if periodo_historico_elements else None

    # Extract nested fields
    poblacion = monumento.find('poblacion')
    localidad = poblacion.findtext('localidad', default=None) if poblacion else None
    provincia = poblacion.findtext('provincia', default=None) if poblacion else None
    municipio = poblacion.findtext('municipio', default=None) if poblacion else None

    coordenadas = monumento.find('coordenadas')
    latitud = coordenadas.findtext('latitud', default=None) if coordenadas else None
    longitud = coordenadas.findtext('longitud', default=None) if coordenadas else None

    # Add data to the dictionary
    data['nombre'].append(nombre)
    data['tipoMonumento'].append(tipo_monumento)
    data['clasificacion'].append(clasificacion)
    data['tipoConstruccion'].append(tipo_construccion)
    data['codigo_postal'].append(codigo_postal)
    data['descripcion'].append(descripcion)
    data['periodoHistorico'].append(periodo_historico)
    data['latitud'].append(latitud)
    data['longitud'].append(longitud)
    data['web'].append(None)  # Placeholder, not in XML
    data['localidad'].append(localidad)
    data['provincia'].append(provincia)
    data['municipio'].append(municipio)

# Create a DataFrame
df_result = pd.DataFrame(data)

# Save as JSON with None explicitly converted to null
df_result.to_json(
    '../Resultados/XMLtoJSON.json',
    orient='records',
    force_ascii=False,
    default_handler=str
)

# Print the DataFrame
print(df_result.head())
