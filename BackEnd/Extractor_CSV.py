import pandas as pd

# Leer el archivo CSV
csv_path = '../Fuentes_de_datos/Comunitat_Valenciana/vcl.csv'
df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')

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

# Función para clasificar el tipo de monumento basado en la denominación
def get_tipo_monumento(denominacion):
    denominacion = denominacion.lower()
    if "yacimiento" in denominacion:
        return "Yacimiento arquelógico"
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

# Extraer información de cada fila del CSV
for _, row in df.iterrows():
    nombre = row['DENOMINACION']
    tipo_monumento = get_tipo_monumento(nombre)
    clasificacion = row['CLASIFICACION']
    
    # Asignar valores adicionales, si no están disponibles se asigna pd.NA
    tipo_construccion = pd.NA  # No hay columna para esto en el CSV, puedes agregar un valor si se conoce la lógica
    codigo_postal = pd.NA  # No hay columna para esto en el CSV
    descripcion = pd.NA  # No hay columna para esto en el CSV
    periodo_historico = pd.NA  # No hay columna para esto en el CSV
    latitud = row['UTMNORTE'] if pd.notnull(row['UTMNORTE']) else pd.NA
    longitud = row['UTMESTE'] if pd.notnull(row['UTMESTE']) else pd.NA
    web = pd.NA  # No hay columna para esto en el CSV
    localidad = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else pd.NA
    provincia = row['PROVINCIA'] if pd.notnull(row['PROVINCIA']) else pd.NA
    municipio = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else pd.NA

    # Añadir los datos al diccionario
    data['nombre'].append(nombre)
    data['tipoMonumento'].append(tipo_monumento)
    data['clasificacion'].append(clasificacion)
    data['tipoConstruccion'].append(tipo_construccion)
    data['codigo_postal'].append(codigo_postal)
    data['descripcion'].append(descripcion)
    data['periodoHistorico'].append(periodo_historico)
    #REALIZAR CONVERSION DESDE UTM A WGS CON SELENIUM A ALGUNA WEB
    data['latitud'].append(latitud)
    data['longitud'].append(longitud)
    data['web'].append(web)
    data['localidad'].append(localidad)
    data['provincia'].append(provincia)
    data['municipio'].append(municipio)

# Crear un DataFrame con los datos extraídos
df_result = pd.DataFrame(data)

# Mostrar el DataFrame resultante
print(df_result.head())



# Guardar los datos en formato JSON (opcional)
df_result.to_json('../Resultados/CSVtoJSON.json', orient='records', force_ascii=False, default_handler=str)
