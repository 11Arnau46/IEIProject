import pandas as pd

# Leer el archivo CSV
csv_path = '../Fuentes_de_datos/Comunitat_Valenciana/vcl.csv'
df = pd.read_csv(csv_path, delimiter=';', encoding='utf-8')

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

# Función para clasificar el tipo de monumento basado en la denominación
def get_tipo_monumento(denominacion):
    denominacion = denominacion.lower()
    palabras_clave = {
        "Yacimiento arquelógico": ["yacimiento", "Yacimiento"],
        "Monasterio-Convento": ["monasterio", "Monasterio", "convento", "Convento"],
        "Iglesia-Ermita": ["iglesia", "Iglesia", "ermita", "Ermita", "catedral", "Catedral", "basílica", "Basílica"],
        "Castillo-Fortaleza-Torre": ["castillo", "Castillo", "fortaleza", "Fortaleza", "torre", "Torre"],
        "Edificio Singular": ["jardín", "Jardín", "palacio", "Palacio"],
        "Puente": ["puente", "Puente"]
    }
    
    for tipo, keywords in palabras_clave.items():
        if any(keyword in denominacion for keyword in keywords):
            return tipo
    return "Otros"

# Extraer información de cada fila del CSV
for _, row in df.iterrows():
    nomMonumento = row['DENOMINACION']
    tipoMonumento = get_tipo_monumento(nomMonumento)

    # Hay que extraerlo de la web
    direccion = pd.NA 
    codigo_postal = pd.NA
    
    # Hay que tranformar
    latitud = row['UTMNORTE'] if pd.notnull(row['UTMNORTE']) else pd.NA 
    longitud = row['UTMESTE'] if pd.notnull(row['UTMESTE']) else pd.NA
    
    descripcion = row['CLASIFICACION']
    codLocalidad = pd.NA # Hay que generarlo
    nomLocalidad = row['MUNICIPIO'] if pd.notnull(row['MUNICIPIO']) else pd.NA
    codProvincia = pd.NA # Hay que generarlo
    nomProvincia = row['PROVINCIA'] if pd.notnull(row['PROVINCIA']) else pd.NA

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

# Guardar los datos en formato JSON con formato legible
df_con_coords.to_json(
    '../Resultados/CSVtoJSON_con_coords.json',
    orient='records',
    force_ascii=False,
    indent=4,
    default_handler=str
)
if len(df_sin_coords) > 0:
    df_sin_coords.to_json(
        '../Resultados/CSVtoJSON_sin_coords.json',
        orient='records',
        force_ascii=False,
        indent=4,
        default_handler=str
    )
