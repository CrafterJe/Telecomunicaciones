from datetime import datetime
from bson import ObjectId
from app.config import create_app
from app.config.extensions import mongo
from flask import Blueprint, jsonify, request, send_file
from bson.json_util import dumps
import base64
import io

# Crear blueprint para los productos
prod = Blueprint('products', __name__)
app = create_app()

# Obtener todos los productos
@prod.route('/productos/get_all', methods=['GET'])
def listar_prod():
    data = mongo.db.productos.find({})
    r = []
    for producto in data:
        producto['_id'] = str(producto['_id'])
        if 'imagen' in producto:
            producto['imagen'] = True  # Marcar que sí tiene imagen
        else:
            producto['imagen'] = False
        r.append(producto)
    v = dumps(r)
    return v

# Obtener la imagen de un producto específico
@prod.route('/productos/<producto_id>/imagen', methods=['GET'])
def obtener_imagen(producto_id):
    try:
        producto = mongo.db.productos.find_one({'_id': ObjectId(producto_id)})

        if not producto or 'imagen' not in producto:
            return jsonify({"error": "Imagen no encontrada"}), 404

        imagen_data = producto['imagen']

        # Verificar si la imagen es un diccionario con formato MongoDB
        if isinstance(imagen_data, dict) and '$binary' in imagen_data:
            imagen_base64 = imagen_data['$binary']['base64']
        # Verificar si es una cadena válida en base64
        elif isinstance(imagen_data, str) and len(imagen_data) > 0:
            imagen_base64 = imagen_data
        else:
            return jsonify({"error": f"Formato de imagen no válido para el producto {producto_id}"}), 400

        # Corregir padding de Base64 si es necesario
        missing_padding = len(imagen_base64) % 4
        if missing_padding != 0:
            imagen_base64 += '=' * (4 - missing_padding)

        # Convertir de Base64 a bytes
        imagen_bytes = base64.b64decode(imagen_base64)
        return send_file(io.BytesIO(imagen_bytes), mimetype='image/jpeg')

    except Exception as e:
        print(f"❌ Error al obtener la imagen: {str(e)}")
        return jsonify({"error": f"Error al procesar la imagen: {str(e)}"}), 500
