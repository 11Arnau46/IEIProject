import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

def scrape_postal_codes(output_dir='Resultados'):
    try:
        print("\n=== Iniciando el proceso de scraping ===")
        print("Configurando el navegador Edge...")
        # Configurar el driver de Selenium con Edge
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        # Usar webdriver-manager para gestionar el EdgeDriver
        print("Instalando/Actualizando EdgeDriver...")
        service = Service(EdgeChromiumDriverManager().install())
        driver = webdriver.Edge(service=service, options=options)
        
        # URL principal
        print("\nAccediendo a la página principal de Castilla y León...")
        url = "https://es.gpspostcode.com/codigo-postal/spain/pais_vasco/"
        driver.get(url)
        
        print("Esperando a que la página cargue...")
        # Esperar a que la tabla principal se cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table_milieu"))
        )
        
        # Obtener todas las provincias
        print("\nExtrayendo lista de provincias...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', class_='table_milieu')
        rows = table.find_all('tr')[1:]  # Ignorar la primera fila
        print(f"Se encontraron {len(rows)} provincias")
        
        all_data = []
        provincias_procesadas = 0
        
        # Iterar sobre cada provincia
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                provincia_link = cols[2].find('a')
                if provincia_link:
                    provincia_nombre = provincia_link.text
                    provincia_url = provincia_link['href']
                    provincias_procesadas += 1
                    print(f"\n[{provincias_procesadas}/{len(rows)}] Procesando provincia: {provincia_nombre}")
                    
                    # Navegar a la página de la provincia
                    print(f"  Accediendo a la URL de {provincia_nombre}...")
                    driver.get(provincia_url)
                    time.sleep(2)  # Esperar a que la página cargue
                    
                    # Obtener datos de las ciudades
                    ciudad_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    ciudad_table = ciudad_soup.find('table', class_='table_milieu')
                    if ciudad_table:
                        ciudad_rows = ciudad_table.find_all('tr')[1:]
                        print(f"  Encontradas {len(ciudad_rows)} ciudades en {provincia_nombre}")
                        ciudades_procesadas = 0
                        
                        for ciudad_row in ciudad_rows:
                            ciudad_cols = ciudad_row.find_all('td')
                            if len(ciudad_cols) >= 5:
                                try:
                                    codigo_postal = ciudad_cols[1].text.strip()
                                    nombre_ciudad = ciudad_cols[2].text.strip()
                                    x = ciudad_cols[3].text.strip()  # Coordenada X
                                    y = ciudad_cols[4].text.strip()  # Coordenada Y
                                    
                                    data = {
                                        'provincia': provincia_nombre,
                                        'codigo_postal': codigo_postal,
                                        'ciudad': nombre_ciudad,
                                        'x': x,
                                        'y': y
                                    }
                                    all_data.append(data)
                                    ciudades_procesadas += 1
                                    if ciudades_procesadas % 10 == 0:  # Mostrar progreso cada 10 ciudades
                                        print(f"    Procesadas {ciudades_procesadas}/{len(ciudad_rows)} ciudades...")
                                except Exception as e:
                                    print(f"    Error procesando ciudad en {provincia_nombre}: {e}")
                        
                        print(f"  ✓ Completada provincia {provincia_nombre}: {ciudades_procesadas} ciudades procesadas")
        
        print("\nCerrando el navegador...")
        driver.quit()
        
        # Crear directorio si no existe
        print(f"\nCreando directorio de salida: {output_dir}")
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar los datos en un archivo JSON
        output_file = os.path.join(output_dir, 'codigos_postales_eus.json')
        print(f"Guardando datos en {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
        
        print(f"\n=== Proceso completado con éxito ===")
        print(f"Total de registros procesados: {len(all_data)}")
        print(f"Datos guardados en: {output_file}")
        return all_data
        
    except Exception as e:
        print(f"\n❌ Error durante el scraping: {e}")
        if 'driver' in locals():
            print("Cerrando el navegador debido al error...")
            driver.quit()
        return None

if __name__ == "__main__":
    scrape_postal_codes() 