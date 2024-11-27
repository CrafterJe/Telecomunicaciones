from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
from flask import Blueprint, jsonify
from flask import request

cart = Blueprint('cart', __name__)
app = create_app()

@cart.route('/carrito/<user_id>', methods=['GET'])
def obtener_carrito(user_id):
    # Obtener el carrito de compras para un usuario
    carrito = mongo.db.carrito.find_one({"usuario_id": user_id})  # Usamos usuario_id en lugar de _id
    if carrito:
        return jsonify(carrito), 200  # Devuelves el carrito completo
    else:
        return jsonify({"message": "Carrito vacío o no encontrado"}), 404

@cart.route('/carrito/<user_id>', methods=['POST'])
def agregar_al_carrito(user_id):
    # Agregar un producto al carrito del usuario
    data = request.json  # Producto a agregar al carrito
    producto = data.get('producto')

    # Buscar el carrito existente del usuario
    carrito = mongo.db.carrito.find_one({"usuario_id": user_id})

    if carrito:
        # Si el carrito existe, se agrega el producto o se incrementa la cantidad
        productos = carrito['productos']
        total = carrito['total']  # Recalcular el total
        for item in productos:
            if item['_id'] == producto['_id']:
                item['cantidad'] += producto['cantidad']
                total += producto['precio_unitario'] * producto['cantidad']
                break
        else:
            # Si no está en el carrito, se agrega
            productos.append(producto)
            total += producto['precio_unitario'] * producto['cantidad']

        # Actualizar el carrito en la base de datos
        mongo.db.carrito.update_one(
            {"usuario_id": user_id},
            {"$set": {"productos": productos, "total": total, "fecha": datetime.utcnow()}}
        )
    else:
        # Si no existe un carrito, se crea uno nuevo
        mongo.db.carrito.insert_one({
            "usuario_id": user_id,
            "productos": [producto],
            "total": producto['precio_unitario'] * producto['cantidad'],  # Iniciar con el precio del primer producto
            "fecha": datetime.utcnow()
        })
    
    return jsonify({"message": "Producto agregado al carrito", "total": total}), 200
