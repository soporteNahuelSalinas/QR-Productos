import os
import re
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Configuración general
dpi = 300
a4_width, a4_height = int(8.27 * dpi), int(11.69 * dpi)
card_width, card_height = 780, 340
output_folder = "output_pdfs"
qr_folder = "qrcodes-manuales"
page_color = "#D4C3C3"
qr_max_height = card_height - int(0.1 * dpi + 2)
background_color = "#FFFF"
font_color = "black"
margin = int(0.01 * dpi)
spacing = int(0.02 * dpi)
columns = 3
max_rows_per_page = 10

# Ruta relativa a la fuente en tu proyecto
font_path = os.path.join("assets", "fonts", "Poppins-Regular.ttf")
if not os.path.exists(font_path):
    raise FileNotFoundError(f"No se encontró la fuente en la ubicación especificada: {font_path}")

# Crear la fuente
font_size = 30
font = ImageFont.truetype(font_path, font_size)

def clean_product_name(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r"[_-]", " ", name)
    name = re.sub(r"[^\w\s]", "", name)
    
    match = re.search(r'(\d+)$', name)
    reference = match.group(0) if match else ""
    clean_name = re.sub(r'\d+$', '', name).strip()

    return clean_name.strip(), reference.strip()

def generate_cards():
    # Crear carpeta de salida si no existe
    os.makedirs(output_folder, exist_ok=True)
    if not os.path.exists(qr_folder):
        raise FileNotFoundError(f"No se encontró el directorio de QR: {qr_folder}")

    # Obtener nombres de productos y rutas de los QR
    product_data = []
    for file in os.listdir(qr_folder):
        if file.endswith(".png"): 
            product_name, reference = clean_product_name(file)
            product_data.append({"name": product_name, "reference": reference, "qr_path": os.path.join(qr_folder, file)})

    # Inicializar variables para la generación de PDFs
    page_count = 1
    x_offset, y_offset = margin, margin
    current_row = 0
    page = Image.new("RGB", (a4_width, a4_height), page_color)

    # Crear las tarjetas y páginas
    for i, product in enumerate(product_data):
        # Crear tarjeta
        card = Image.new("RGB", (card_width, card_height), background_color)
        card_draw = ImageDraw.Draw(card)

        # Añadir QR
        qr = Image.open(product["qr_path"])
        qr_width = int(qr.width * (qr_max_height / qr.height))
        qr = qr.resize((qr_width, qr_max_height))
        qr_x = card_width - qr.width - margin
        qr_y = (card_height - qr.height) // 2
        card.paste(qr, (qr_x, qr_y))

        # Ajustar el ancho máximo del texto
        text_max_width = card_width - qr_width - margin * 3
        text_x_center_area = (card_width - qr_width - text_max_width) // 2 + 15
        text_y = margin

        # Ajustar el texto a líneas y truncar si es necesario
        wrapped_text = product["name"]
        if len(wrapped_text) > 100:
            wrapped_text = textwrap.shorten(wrapped_text, width=100, placeholder="...")

        if product["reference"]:
            wrapped_text += f" (Ref: {product['reference']})"

        wrapped_text = textwrap.fill(wrapped_text, width=25)

        text_bbox = card_draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]

        text_x = text_x_center_area + (text_max_width - text_width) // 2
        text_y = (card_height - text_height) // 2

        # Dibuja el texto en la tarjeta
        card_draw.multiline_text(
            (text_x, text_y),
            wrapped_text,
            font=font,
            fill=font_color,
            align="center"
        )

        # Pegar tarjeta en la hoja
        page.paste(card, (x_offset, y_offset))

        # Actualizar las coordenadas para la siguiente tarjeta
        x_offset += card_width + spacing

        # Comprobar si hemos alcanzado el número de columnas
        if (i + 1) % columns == 0:
            x_offset = margin
            y_offset += card_height + spacing
            current_row += 1

        # Comprobar si hemos alcanzado el máximo de filas por página
        if current_row >= max_rows_per_page:
            # Guardar la página actual como PDF
            output_file = os.path.join(output_folder, f"tarjetas_qr_pagina_{page_count}.pdf")
            page.save(output_file, resolution=dpi)
            print(f"Página {page_count} guardada en {output_file}")

            # Preparar nueva página
            page_count += 1
            page = Image.new("RGB", (a4_width, a4_height), page_color)
            x_offset, y_offset = margin, margin 
            current_row = 0 

    # Guardar la última hoja si no está vacía
    if x_offset != margin or y_offset != margin:
        output_file = os.path.join(output_folder, f"tarjetas_qr_pagina_{page_count}.pdf")
        page.save(output_file, resolution=dpi)
        print(f"Página {page_count} guardada en {output_file}")

    print("Generación de tarjetas completa.")

# Si quieres que este archivo se ejecute directamente, puedes agregar esto:
if __name__ == "__main__":
    generate_cards()