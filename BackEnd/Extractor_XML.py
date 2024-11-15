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
    if "Yacimiento" in denominacion:
        return "Yacimiento arquelógico"
    elif "Monasterio" in denominacion or "Convento" in denominacion:
        return "Monasterio-Convento"
    elif "Iglesia" in denominacion or "Ermita" in denominacion or "Catedral" in denominacion or "Basílica" in denominacion:
        return "Iglesia-Ermita"
    elif "Castillo" in denominacion or "Fortaleza" in denominacion or "Torre" in denominacion:
        return "Castillo-Fortaleza-Torre"
    elif "Jardín" in denominacion or "Palacio" in denominacion:
        return "Edificio Singular"
    elif denominacion.startswith("Puente"):
        return "Puente"
    else:
        return "Otros"

# Extraer información de cada fila del CSV
for _, row in df.iterrows():
    nombre = row['DENOMINACION']
    tipo_monumento = get_tipo_monumento(nombre)
    clasificacion = row['CLASIFICACION']
    
    # Asignar valores adicionales, si no están disponibles se asigna None
    tipo_construccion = None  # No hay columna para esto en el CSV, puedes agregar un valor si se conoce la lógica
    codigo_postal = None  # No hay columna para esto en el CSV
    descripcion = None  # No hay columna para esto en el CSV
    periodo_historico = None  # No hay columna para esto en el CSV
    latitud = row['UTMNORTE'] if pd.notnull(row['UTMNORTE']) else None
    longitud = row['UTMESTE'] if pd.notnull(row['UTMESTE']) else None
    web = None  # No hay columna para esto en el CSV
    localidad = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else None
    provincia = row['PROVINCIA'] if pd.notnull(row['PROVINCIA']) else None
    municipio = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else None

    # Añadir los datos al diccionario
    data['nombre'].append(nombre)
    data['tipoMonumento'].append(tipo_monumento)
    data['clasificacion'].append(clasificacion)
    data['tipoConstruccion'].append(tipo_construccion)
    data['codigo_postal'].append(codigo_postal)
    data['descripcion'].append(descripcion)
    data['periodoHistorico'].append(periodo_historico)
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

# Guardar el DataFrame a un archivo CSV (opcional)
df_result.to_csv('../Resultados/CSVtoJSON.csv', index=False, encoding='utf-8')

# Guardar los datos en formato JSON (opcional)
df_result.to_json('../Resultados/CSVtoJSON.json', orient='records', lines=True, force_ascii=False)
