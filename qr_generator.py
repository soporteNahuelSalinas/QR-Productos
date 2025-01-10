import json
import requests
from requests.auth import HTTPBasicAuth
import qrcode
import os
import xml.etree.ElementTree as ET
import re

# Configuraciones de la API
api_url = 'https://tienda.anywayinsumos.com.ar/api/products/'
api_key = '7FBXGUHYR2PXIGBS7GC3AAQ7BHEQX57E'
tinyurl_api_url = 'http://tinyurl.com/api-create.php?url='  # URL de la API de TinyURL

# Función para limpiar nombres de archivos
def clean_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name)
    return name.strip()

# Función para generar códigos QR
def generate_qr_codes(product_ids):
    output_dir = 'qrcodes-manuales'
    os.makedirs(output_dir, exist_ok=True)

    for product_id in product_ids:
        url = f"{api_url}{product_id}"
        response = requests.get(url, auth=HTTPBasicAuth(api_key, ''))

        if response.status_code == 200:
            try:
                root = ET.fromstring(response.content)
                product_name_element = root.find('.//name/language')
                product_name = product_name_element.text if product_name_element is not None else None
                
                link_rewrite_element = root.find('.//link_rewrite/language')
                link_rewrite = link_rewrite_element.text if link_rewrite_element is not None else None
                
                reference_element = root.find('.//reference')
                product_reference = reference_element.text if reference_element is not None else None
                
                if product_name is None or link_rewrite is None or product_reference is None:
                    print(f"Error: No se encontró el nombre, link_rewrite o referencia para el producto ID: {product_id}.")
                    continue
                
                product_url = f"https://tienda.anywayinsumos.com.ar/{link_rewrite}/{product_id}-{link_rewrite}.html"
                
                # Solicitar URL acortada
                response_tinyurl = requests.get(tinyurl_api_url + product_url)
                if response_tinyurl.status_code == 200:
                    short_url = response_tinyurl.text
                    print(f"URL acortada: {short_url}")

                    # Generar el código QR
                    qr_img = qrcode.make(short_url)
                    cleaned_name = clean_filename(product_name)
                    qr_filename = os.path.join(output_dir, f"{cleaned_name}_{product_reference}.png")
                    qr_img.save(qr_filename)

                    print(f"Código QR generado y guardado como '{qr_filename}'.")
                else:
                    print(f"Error al acortar la URL: {response_tinyurl.status_code}. Respuesta: {response_tinyurl.text}")

            except ET.ParseError:
                print(f"Error al parsear el XML para el producto {product_id}. Respuesta: {response.text}")
        else:
            print(f"Error al obtener el producto {product_id}: {response.status_code}")
            print("Contenido de la respuesta:", response.text)

# Llamada a la función con una lista de IDs de productos
# generate_qr_codes([1, 2, 3])  # Ejemplo de llamada
