import datetime
from flask import Blueprint, request, jsonify
from app.config.extensions import mongo
from bson import ObjectId
import jwt
from functools import wraps
# Crear el Blueprint para el carrito
cart = Blueprint('carrito', __name__)

def get_user_id_from_token(token):
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return decoded_token.get('user_id')
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def convertir_objectid_a_str(documento):
    """Convierte ObjectId a cadena dentro de un documento o lista."""
    if isinstance(documento, dict):
        return {key: str(value) if isinstance(value, ObjectId) else value for key, value in documento.items()}
    elif isinstance(documento, list):
        return [convertir_objectid_a_str(item) for item in documento]
    return documento

@cart.route('/<user_id>', methods=['GET'])
def obtener_carrito(user_id):
    try:
        print(f"ID del usuario recibido: {user_id}")
        carrito = mongo.db.carrito.find_one({"usuario_id": ObjectId(user_id)})
        
        if not carrito:
            return jsonify({"error": "Carrito no encontrado"}), 404
        
        # Convertir ObjectId a string
        carrito['_id'] = str(carrito['_id'])
        carrito['usuario_id'] = str(carrito['usuario_id'])
        for producto in carrito['productos']:
            producto['_id'] = str(producto['_id'])

        print("Carrito encontrado:", carrito)  # Debugging
        return jsonify(carrito), 200
    except Exception as e:
        print("Error al obtener carrito:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500
# Agregar un producto al carrito

def convertir_objectid_a_str(obj):
    """Convierte recursivamente todos los ObjectId en un objeto a string."""
    if isinstance(obj, dict):
        return {k: convertir_objectid_a_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_objectid_a_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)  # Convierte el ObjectId a string
    return obj

@cart.route('/agregar', methods=['POST'])
def agregar_al_carrito():
    try:
        print("Solicitud recibida en /carrito/agregar")
        data = request.get_json()
        print("Datos recibidos:", data)

        user_id = data.get('userId')
        producto_id = data.get('productoId')
        cantidad = data.get('cantidad')

        if not user_id or not producto_id or not isinstance(cantidad, int) or cantidad <= 0:
            print("Datos de entrada inválidos")
            return jsonify({"error": "Datos de entrada inválidos"}), 400

        user_id_obj = ObjectId(user_id)
        carrito_usuario = mongo.db.carrito.find_one({"usuario_id": user_id_obj})
        if not carrito_usuario:
            return jsonify({"error": "Carrito no encontrado"}), 404

        producto = mongo.db.productos.find_one({"_id": ObjectId(producto_id)})
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        if "stock" not in producto or producto["stock"] < cantidad:
            return jsonify({"error": "Stock insuficiente"}), 400

        # Agregar el producto al carrito sin modificar el stock
        producto_existente = next(
            (p for p in carrito_usuario['productos'] if str(p['_id']) == producto_id), None)

        if producto_existente:
            producto_existente['cantidad'] += cantidad
        else:
            carrito_usuario['productos'].append({
                "_id": producto["_id"],
                "nombre": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"]
            })

        carrito_usuario['total'] = sum(
            p['cantidad'] * p['precio'] for p in carrito_usuario['productos'])

        mongo.db.carrito.update_one(
            {"_id": carrito_usuario["_id"]},
            {"$set": {"productos": carrito_usuario["productos"], "total": carrito_usuario["total"]}}
        )

        return jsonify({"message": "Producto agregado al carrito"}), 200

    except Exception as e:
        print("Error en /carrito/agregar:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500

# Eliminar un producto del carrito
@cart.route('/<user_id>/producto/<producto_id>', methods=['DELETE'])
def eliminar_producto(user_id, producto_id):
    try:
        carrito = mongo.db.carrito.find_one({"usuario_id": ObjectId(user_id)})
        if not carrito:
            return jsonify({"error": "Carrito no encontrado"}), 404

        carrito['productos'] = [p for p in carrito['productos'] if str(p['_id']) != producto_id]
        carrito['total'] = sum(p['precio'] * p['cantidad'] for p in carrito['productos'])

        mongo.db.carrito.update_one(
            {"_id": carrito['_id']},
            {"$set": {"productos": carrito['productos'], "total": carrito['total']}}
        )

        return jsonify({"message": "Producto eliminado"}), 200
    except Exception as e:
        return jsonify({"error": "Error al eliminar el producto"}), 500

# Actualizar la cantidad de un producto en el carrito
@cart.route('/actualizar', methods=['POST'])
def actualizar_producto():
    try:
        data = request.get_json()

        # Validar datos recibidos
        user_id = data.get('usuario_id')
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad')

        if not user_id or not producto_id or not cantidad:
            return jsonify({"error": "Faltan datos necesarios"}), 400

        # Buscar el carrito del usuario
        carrito = mongo.db.carrito.find_one({"usuario_id": ObjectId(user_id)})
        if not carrito:
            return jsonify({"error": "Carrito no encontrado"}), 404

        # Buscar el producto en el carrito
        producto_en_carrito = next(
            (p for p in carrito['productos'] if str(p['_id']) == producto_id), None
        )

        if not producto_en_carrito:
            return jsonify({"error": "Producto no encontrado en el carrito"}), 404

        # Actualizar la cantidad del producto
        producto_en_carrito['cantidad'] = cantidad

        # Recalcular el total
        carrito['total'] = sum(
            p['precio'] * p['cantidad'] for p in carrito['productos']
        )

        # Actualizar el carrito en la base de datos
        mongo.db.carrito.update_one(
            {"usuario_id": ObjectId(user_id)},
            {"$set": {"productos": carrito['productos'], "total": carrito['total']}}
        )

        # Responder con el carrito actualizado
        return jsonify({"message": "Cantidad del producto actualizada", "carrito": convertir_objectid_a_str(carrito)}), 200

    except Exception as e:
        print("Error en actualizar_producto:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500
