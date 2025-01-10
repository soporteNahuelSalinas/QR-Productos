from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from qr_generator import generate_qr_codes
from generate_product_cards import generate_cards


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Cambia esto por una clave secreta segura

# Ruta para la página principal
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']  # Obtenemos el archivo CSV
        if file and file.filename.endswith('.csv'):
            # Leer el archivo CSV y extraer los IDs de productos
            ids_productos = []
            csv_file = csv.DictReader(file.stream.read().decode('utf-8').splitlines(), delimiter=';')
            for row in csv_file:
                ids_productos.append(row['Product ID'])
            
            # Guardar los IDs en un archivo JSON
            with open('data/products.json', 'w', encoding='utf-8') as json_file:
                json.dump(ids_productos, json_file)

            flash('Archivo CSV cargado y IDs extraídos exitosamente.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Por favor, carga un archivo CSV válido.', 'error')

    return render_template('index.html')

# Ruta para generar códigos QR
@app.route('/generate', methods=['POST'])
def generate():
    with open('data/products.json', 'r', encoding='utf-8') as json_file:
        product_ids = json.load(json_file)

    if not product_ids:
        flash('No se encontraron IDs de productos.', 'error')
        return redirect(url_for('index'))

    # Llamar a la función para generar códigos QR
    generate_qr_codes(product_ids)

    flash('Códigos QR generados exitosamente.', 'success')
    return redirect(url_for('index'))

@app.route("/generate_cards", methods=["POST"])
def generate_cards_route():
    try:
        # Llama a la función que genera las tarjetas
        generate_cards()  # Asegúrate de que esta función exista en tu script
        flash("Tarjetas de productos generadas con éxito.", "success")
    except Exception as e:
        flash(f"Error al generar las tarjetas: {str(e)}", "error")
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True)