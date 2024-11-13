import xml.etree.ElementTree as ET
import pandas as pd

# Parsear el archivo XML
tree = ET.parse('../Fuentes_de_datos/Castilla_i_leon/cle.xml')
root = tree.getroot()

# Listas para almacenar los datos extraídos
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
    'web': []
}

# Diccionario de mapeo para el tipo de monumento a los valores de TipoEnum
tipo_mapping = {
    "Yacimientos arqueológicos": "YacimientoArqueologico",
    "Iglesia Ermita": "IglesiaErmita",
    "Monasterio Convento": "MonasterioConvento",
    "Castillo Fortaleza Torre": "CastilloFortalezaTorre",
    "Edificio Singular": "EdificioSingular",
    "Puente": "Puente",
    "Otros": "Otros"
}

# Extraer información de cada monumento
for monumento in root.findall('monumento'):
    nombre = monumento.find('nombre')
    if nombre is not None:
        data['nombre'].append(nombre.text)
    else:
        data['nombre'].append(None)

    # Convertir el tipo de monumento al formato del enum
    tipo_monumento = monumento.find('tipoMonumento')
    if tipo_monumento is not None:
        data['tipoMonumento'].append(tipo_mapping.get(tipo_monumento.text, "Otros"))
    else:
        data['tipoMonumento'].append("Otros")  # Valor por defecto si no existe

    clasificacion = monumento.find('clasificacion')
    if clasificacion is not None:
        data['clasificacion'].append(clasificacion.text)
    else:
        data['clasificacion'].append(None)

    tipo_construccion = monumento.find('tipoConstruccion')
    if tipo_construccion is not None:
        data['tipoConstruccion'].append(tipo_construccion.text)
    else:
        data['tipoConstruccion'].append(None)

    # Manejo de 'codigoPostal'
    codigo_postal = monumento.find('codigoPostal')
    if codigo_postal is not None:
        data['codigo_postal'].append(codigo_postal.text)
    else:
        data['codigo_postal'].append(None)

    # Procesar la descripción (CDATA)
    descripcion = monumento.find('Descripcion')
    if descripcion is not None:
        data['descripcion'].append(descripcion.text.strip() if descripcion.text else None)
    else:
        data['descripcion'].append(None)

    # Procesar los períodos históricos (pueden haber múltiples)
    periodos = [periodo.text for periodo in monumento.findall('periodoHistorico')]
    data['periodoHistorico'].append('; '.join(periodos) if periodos else None)

    # Procesar coordenadas
    coordenadas = monumento.find('coordenadas')
    if coordenadas is not None:
        latitud = coordenadas.find('latitud')
        longitud = coordenadas.find('longitud')
        data['latitud'].append(latitud.text if latitud is not None else None)
        data['longitud'].append(longitud.text if longitud is not None else None)
    else:
        data['latitud'].append(None)
        data['longitud'].append(None)

    # Procesar web (opcional)
    web = monumento.find('web')
    data['web'].append(web.text if web is not None else None)

# Crear un DataFrame de pandas
df = pd.DataFrame(data)

# Mostrar el DataFrame resultante
print(df)

# Guardar el DataFrame a un archivo CSV (opcional, para inspección)
df.to_json('../Resultados/XMLtoJSON.json', orient='records', lines=True, force_ascii=False)