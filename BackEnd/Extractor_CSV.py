import pandas as pd
import Coords_converter
import json
import API2

# Leer el archivo CSV
csv_path = '../Fuentes_de_datos/Demo/vcl.csv'
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
        "YacimientoArquelogico": ["yacimiento", "Yacimiento"],
        "MonasterioConvento": ["monasterio", "Monasterio", "convento", "Convento"],
        "IglesiaErmita": ["iglesia", "Iglesia", "ermita", "Ermita", "catedral", "Catedral", "basílica", "Basílica"],
        "CastilloFortalezaTorre": ["castillo", "Castillo", "fortaleza", "Fortaleza", "torre", "Torre"],
        "EdificioSingular": ["jardín", "Jardín", "palacio", "Palacio"],
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

#Hacer conversión de coordenadas a grados con Selenium
#https://www.ign.es/web/calculadora-geodesica

ruta_json_entrada = "../Resultados/CSVtoJSON_con_coords.json"  # Cambia por tu archivo JSON
ruta_json_salida = "../Resultados/CSVtoJSON_Corregido.json"

with open(ruta_json_entrada, "r", encoding="utf-8") as file:
    monumentos = json.load(file)

# Actualiza los datos del JSON
for monumento in monumentos:
    if monumento["latitud"] and monumento["longitud"]:
        print(f"Convirtiendo coordenadas UTM para {monumento['nomMonumento']}...")
        lat, lon = Coords_converter.convert_utm(monumento["latitud"], monumento["longitud"])
        if lat and lon:
            monumento["latitud"] = lat
            monumento["longitud"] = lon

# Guarda el archivo actualizado
with open(ruta_json_salida, "w", encoding="utf-8") as file:
    json.dump(monumentos, file, ensure_ascii=False, indent=4)

print(f"Archivo actualizado guardado en {ruta_json_salida}.")



#Usar la API para obtener el Código Postal y Localidad
#https://opencagedata.com/api correo es swappypin@gmail.com y la contraseña es proyectoiei
#2500 Llamadas diarias

#Añadirlo al JSON resultante

