import datetime
from flask import Blueprint, request, jsonify
from app.config.extensions import mongo
from bson import ObjectId
import jwt
from app.blueprints.decorators import auth_required

# Crear el Blueprint para el carrito
cart = Blueprint('carrito', __name__)

def convertir_objectid_a_str(obj):
    """Convierte recursivamente todos los ObjectId en un objeto a string."""
    if isinstance(obj, dict):
        return {k: convertir_objectid_a_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convertir_objectid_a_str(item) for item in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)  
    return obj

def calcular_subtotal_y_total(productos):
    """Calcula el subtotal y total asegurando siempre 2 decimales."""
    subtotal = sum(float(p['cantidad']) * float(p['precio']) for p in productos)
    subtotal = round(subtotal, 2)  # Asegurar 2 decimales
    
    total = round(subtotal * 1.16, 2)  # Aplicar 16% IVA
    
    return float(f"{subtotal:.2f}"), float(f"{total:.2f}")  # Convertir a string y luego a float para mantener decimales

@cart.route('/<user_id>', methods=['GET'])
@auth_required
def obtener_carrito(user_id):
    """Obtener el carrito de compras del usuario."""
    try:
        carrito = mongo.db.carrito.find_one({"usuario_id": ObjectId(user_id)})
        if not carrito:
            return jsonify({"error": "Carrito no encontrado"}), 404

        # Asegurar que subtotal y total siempre estén en la respuesta
        carrito.setdefault("subtotal", 0.00)
        carrito.setdefault("total", 0.00)

        carrito = convertir_objectid_a_str(carrito)
        return jsonify(carrito), 200
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500


@cart.route('/agregar', methods=['POST'])
@auth_required
def agregar_al_carrito():
    """Agregar un producto al carrito sin permitir exceder el stock disponible."""
    try:
        data = request.get_json()
        print("📥 Datos recibidos:", data)  # 🔹 Debugging

        user_id = data.get('userId')
        producto_id = data.get('productoId')
        cantidad = data.get('cantidad')

        if not user_id or not producto_id or not isinstance(cantidad, int) or cantidad <= 0:
            print("❌ Datos de entrada inválidos")
            return jsonify({"error": "Datos de entrada inválidos"}), 200  # ✅ Cambiado de 400 a 200

        user_id_obj = ObjectId(user_id)
        carrito_usuario = mongo.db.carrito.find_one({"usuario_id": user_id_obj})
        if not carrito_usuario:
            print("❌ Carrito no encontrado para el usuario:", user_id)
            return jsonify({"error": "Carrito no encontrado"}), 200  # ✅ Cambiado de 404 a 200

        producto = mongo.db.productos.find_one({"_id": ObjectId(producto_id)})
        if not producto:
            print("❌ Producto no encontrado:", producto_id)
            return jsonify({"error": "Producto no encontrado"}), 200  # ✅ Cambiado de 404 a 200

        print("✅ Producto encontrado:", producto)

        # Verificar stock
        producto_existente = next((p for p in carrito_usuario['productos'] if str(p['_id']) == producto_id), None)
        cantidad_total = cantidad
        if producto_existente:
            cantidad_total += producto_existente['cantidad']

        stock_disponible = producto.get("stock", 0)
        print(f"🔍 Stock disponible: {stock_disponible}, Cantidad solicitada: {cantidad_total}")

        if cantidad_total > stock_disponible:
            print(f"❌ Stock insuficiente. Solo quedan {stock_disponible} unidades disponibles.")
            return jsonify({"message": "error_controlado", "error": f"Stock insuficiente. Solo quedan {stock_disponible} unidades disponibles."}), 200  # ✅ Devuelve un mensaje en 200 OK

        # Si pasa la validación, actualizar o agregar el producto al carrito
        if producto_existente:
            producto_existente['cantidad'] += cantidad
        else:
            carrito_usuario['productos'].append({
                "_id": producto["_id"],
                "nombre": producto["nombre"],
                "cantidad": cantidad,
                "precio": producto["precio"]
            })

        carrito_usuario['subtotal'], carrito_usuario['total'] = calcular_subtotal_y_total(carrito_usuario['productos'])

        mongo.db.carrito.update_one(
            {"_id": carrito_usuario["_id"]},
            {"$set": {"productos": carrito_usuario["productos"], "subtotal": carrito_usuario['subtotal'], "total": carrito_usuario['total']}}
        )

        print("✅ Producto agregado correctamente al carrito.")
        return jsonify({"message": "Producto agregado al carrito"}), 200

    except Exception as e:
        print("❌ Error interno del servidor:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500

@cart.route('/actualizar', methods=['POST'])
@auth_required
def actualizar_producto():
    """Actualizar la cantidad de un producto en el carrito sin exceder el stock."""
    try:
        data = request.get_json()
        user_id = data.get('usuario_id')
        producto_id = data.get('producto_id')
        cantidad = data.get('cantidad')

        if not user_id or not producto_id or not isinstance(cantidad, int) or cantidad <= 0:
            return jsonify({"message": "error_controlado", "error": "Datos de entrada inválidos"}), 200  # ✅ Devuelve 200 OK con mensaje de error

        carrito = mongo.db.carrito.find_one({"usuario_id": ObjectId(user_id)})
        if not carrito:
            return jsonify({"message": "error_controlado", "error": "Carrito no encontrado"}), 200  # ✅ Devuelve 200 OK

        producto_en_carrito = next((p for p in carrito['productos'] if str(p['_id']) == producto_id), None)
        if not producto_en_carrito:
            return jsonify({"message": "error_controlado", "error": "Producto no encontrado en el carrito"}), 200  # ✅ Devuelve 200 OK

        producto_real = mongo.db.productos.find_one({"_id": ObjectId(producto_id)})
        if not producto_real:
            return jsonify({"message": "error_controlado", "error": "Producto no encontrado en la base de datos"}), 200  # ✅ Devuelve 200 OK

        stock_disponible = producto_real.get("stock", 0)

        if cantidad > stock_disponible:
            return jsonify({"message": "error_controlado", "error": f"Stock insuficiente. Solo quedan {stock_disponible} unidades disponibles."}), 200  # ✅ Devuelve 200 OK

        producto_en_carrito['cantidad'] = cantidad

        carrito['subtotal'], carrito['total'] = calcular_subtotal_y_total(carrito['productos'])

        mongo.db.carrito.update_one(
            {"usuario_id": ObjectId(user_id)},
            {"$set": {"productos": carrito['productos'], "subtotal": carrito['subtotal'], "total": carrito['total']}}
        )

        return jsonify({"message": "Cantidad actualizada", "carrito": convertir_objectid_a_str(carrito)}), 200

    except Exception as e:
        print("❌ Error en actualizar_producto:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500


@cart.route('/<user_id>/producto/<producto_id>', methods=['DELETE', 'OPTIONS'])
@auth_required
def eliminar_producto(user_id, producto_id):
    """Eliminar un producto del carrito y recalcular subtotal y total."""
    try:
        print(f"🗑️ Eliminando producto {producto_id} del usuario {user_id}")
        
        carrito = mongo.db.carrito.find_one({"usuario_id": ObjectId(user_id)})
        if not carrito:
            return jsonify({"error": "Carrito no encontrado"}), 404

        # Filtrar producto y recalcular valores
        carrito['productos'] = [p for p in carrito['productos'] if str(p['_id']) != producto_id]
        carrito['subtotal'], carrito['total'] = calcular_subtotal_y_total(carrito['productos'])

        mongo.db.carrito.update_one(
            {"_id": carrito["_id"]},
            {"$set": {"productos": carrito['productos'], "subtotal": carrito['subtotal'], "total": carrito['total']}}
        )

        print("✅ Producto eliminado correctamente")
        return jsonify({"message": "Producto eliminado"}), 200
    except Exception as e:
        print("❌ Error al eliminar producto:", str(e))
        return jsonify({"error": "Error interno del servidor"}), 500
