import pandas as pd
import xml.etree.ElementTree as ET
import re

# Leer el archivo XML
xml_path = '../Fuentes_de_datos/Castilla_i_leon/cle.xml'
tree = ET.parse(xml_path)
root = tree.getroot()

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
    denominacion = denominacion.lower()
    palabras_clave = {
        "Yacimiento arquelógico": ["yacimiento"],
        "Monasterio-Convento": ["monasterio", "convento"],
        "Iglesia-Ermita": ["iglesia", "ermita", "catedral", "basílica"],
        "Castillo-Fortaleza-Torre": ["castillo", "fortaleza", "torre"],
        "Edificio Singular": ["jardín", "palacio"],
        "Puente": ["puente"]
    }
    
    for tipo, keywords in palabras_clave.items():
        if any(keyword in denominacion for keyword in keywords):
            return tipo
    return "Otros"

# Función para limpiar texto HTML
def clean_html_text(text):
    if pd.isna(text):
        return text
    # Eliminar todas las etiquetas HTML
    clean_text = re.sub(r'<[^>]+>', '', text)
    # Reemplazar caracteres especiales HTML
    clean_text = clean_text.replace('&oacute;', 'ó')
    clean_text = clean_text.replace('&aacute;', 'á')
    clean_text = clean_text.replace('&eacute;', 'é')
    clean_text = clean_text.replace('&iacute;', 'í')
    clean_text = clean_text.replace('&uacute;', 'ú')
    clean_text = clean_text.replace('&ntilde;', 'ñ')
    # Eliminar espacios extra y saltos de línea
    clean_text = ' '.join(clean_text.split())
    return clean_text

# Extraer información de cada elemento del XML
for monumento in root.findall('.//monumento'):
    nomMonumento = monumento.find('nombre').text if monumento.find('nombre') is not None else pd.NA
    tipoMonumento = monumento.find('tipoMonumento').text if monumento.find('tipoMonumento') is not None else pd.NA
    
    # Obtener dirección de la calle
    # Las direcciones pueden ser nulas, hay que extraerlas de la web en dicho caso o eliminarlas
    direccion = monumento.find('calle').text if monumento.find('calle') is not None else pd.NA
    codigo_postal = monumento.find('codigoPostal').text if monumento.find('codigoPostal') is not None else pd.NA
    
    # Obtener coordenadas
    coordenadas = monumento.find('coordenadas')
    if coordenadas is not None:
        longitud = coordenadas.find('longitud').text if coordenadas.find('longitud') is not None else pd.NA
        latitud = coordenadas.find('latitud').text if coordenadas.find('latitud') is not None else pd.NA
    else:
        longitud = pd.NA
        latitud = pd.NA
    
    # Obtener descripción
    descripcion = monumento.find('Descripcion').text if monumento.find('Descripcion') is not None else pd.NA
    descripcion = clean_html_text(descripcion)
    
    # Obtener información de población
    poblacion = monumento.find('poblacion')
    if poblacion is not None:
        nomLocalidad = poblacion.find('localidad').text if poblacion.find('localidad') is not None else pd.NA
        nomProvincia = poblacion.find('provincia').text if poblacion.find('provincia') is not None else pd.NA
    else:
        nomLocalidad = pd.NA
        nomProvincia = pd.NA
    
    codLocalidad = pd.NA  # Generar según necesidad
    codProvincia = pd.NA  # Generar según necesidad

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
    '../Resultados/XMLtoJSON_con_coords.json',
    orient='records',
    force_ascii=False,
    indent=4,
    default_handler=str
)
if len(df_sin_coords) > 0:
    df_sin_coords.to_json(
        '../Resultados/XMLtoJSON_sin_coords.json',
        orient='records',
        force_ascii=False,
        indent=4,
        default_handler=str
    )
