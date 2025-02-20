from flask import Blueprint, jsonify, request
from app.config.extensions import mongo
from bson import ObjectId
import jwt
from functools import wraps
from app.blueprints.config import SECRET_KEY


admin_bp = Blueprint('admin', __name__)
admin_prod_bp = Blueprint('admin_productos', __name__)

# Middleware para verificar si el usuario es admin
# 
# Requerir funcion para admin.py asi evitar problemas de seguridad
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            print("❌ No se envió token en la petición")
            return jsonify({"error": "Acceso no autorizado"}), 403

        try:
            print(f"🔍 Token recibido: {token}")  # Verificar el token en consola
            token = token.replace("Bearer ", "")  # Eliminar "Bearer " del token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get("user_id")
            usuario = mongo.db.usuarios.find_one({"_id": ObjectId(user_id)})

            if not usuario:
                print(f"❌ No se encontró el usuario con ID: {user_id}")
                return jsonify({"error": "Acceso denegado"}), 403

            if usuario.get("rol") != "admin":
                print(f"❌ Usuario {usuario['usuario']} no tiene rol de admin")
                return jsonify({"error": "Acceso denegado"}), 403

        except jwt.ExpiredSignatureError:
            print("❌ Token expirado")
            return jsonify({"error": "Token expirado"}), 403
        except jwt.InvalidTokenError:
            print("❌ Token inválido")
            return jsonify({"error": "Token inválido"}), 403
        except Exception as e:
            print(f"❌ Error al procesar token: {str(e)}")
            return jsonify({"error": "Token inválido"}), 403

        return f(*args, **kwargs)

    return decorated_function

# Obtener total de usuarios (solo admins)
@admin_bp.route('/admin/usuarios/total', methods=['GET'])
@admin_required
def total_usuarios():
    total = mongo.db.usuarios.count_documents({})
    return jsonify({"total": total})

# Obtener total de productos en stock (solo admins)
@admin_bp.route('/admin/productos/total', methods=['GET'])
@admin_required
def total_productos():
    total = mongo.db.productos.count_documents({})
    return jsonify({"total": total})

# Obtener lista de usuarios (solo admins)
@admin_bp.route('/admin/usuarios', methods=['GET'])
@admin_required
def obtener_usuarios():
    usuarios = list(mongo.db.usuarios.find({}, {"password": 0}))  # No enviar contraseñas
    for usuario in usuarios:
        usuario["_id"] = str(usuario["_id"])
    return jsonify(usuarios)

# Eliminar usuario por ID (solo admins)
@admin_bp.route('/admin/usuarios/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    token = request.headers.get('Authorization')

    if not token:
        print("❌ No se envió token en la petición")
        return jsonify({"error": "Token de autorización no presente"}), 401

    try:
        token = token.replace("Bearer ", "").strip()
        print(f"🔍 Token recibido en Flask: {token}")

        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")

        if id == user_id:
            return jsonify({"error": "No puedes eliminar tu propio usuario"}), 403

        result = mongo.db.usuarios.delete_one({"_id": ObjectId(id)})
        if result.deleted_count:
            return jsonify({"message": "Usuario eliminado"}), 200
        else:
            return jsonify({"error": "Usuario no encontrado"}), 404

    except jwt.DecodeError:
        print("❌ Error: Token malformado o dañado")
        return jsonify({"error": "Token inválido"}), 403

    except Exception as e:
        print(f"❌ Error en eliminar usuario: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


@admin_bp.route('/admin/usuarios/<id>/rol', methods=['PUT'])
@admin_required
def actualizar_rol(id):
    data = request.json
    print(f"🔹 Datos recibidos para actualizar rol: {data}")  # Ver qué datos llegan

    nuevo_rol = data.get("rol")

    if nuevo_rol not in ["usuario", "admin"]:
        print("❌ Error: Rol inválido")
        return jsonify({"error": "Rol inválido"}), 400

    token = request.headers.get('Authorization')
    token = token.replace("Bearer ", "").strip()
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token.get("user_id")

    # Evitar que un admin se degrade a usuario
    if id == user_id and nuevo_rol == "usuario":
        print("❌ Intento de degradarse a usuario")
        return jsonify({"error": "No puedes cambiarte tu propio rol a usuario"}), 403

    result = mongo.db.usuarios.update_one({"_id": ObjectId(id)}, {"$set": {"rol": nuevo_rol}})

    if result.matched_count:
        print("✅ Rol actualizado correctamente")
        return jsonify({"message": "Rol actualizado"}), 200

    print("❌ Usuario no encontrado")
    return jsonify({"error": "Usuario no encontrado"}), 404

@admin_prod_bp.route('/admin/productos', methods=['GET'])
@admin_required
def obtener_productos():
    productos = list(mongo.db.productos.find({}))
    for producto in productos:
        producto["_id"] = str(producto["_id"])
    return jsonify(productos), 200

# Agregar un nuevo producto
@admin_prod_bp.route('/admin/productos', methods=['POST'])
@admin_required
def agregar_producto():
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get("nombre") or not data.get("tipo") or "precio" not in data:
            return jsonify({"error": "Faltan datos requeridos (nombre, tipo, precio)"}), 400

        # Validar que precio y stock sean números
        try:
            precio = float(data["precio"])
            stock = int(data.get("stock", 0))
        except ValueError:
            return jsonify({"error": "El precio debe ser un número y el stock un entero"}), 400

        # Validar que `especificaciones` sea un diccionario ('Arreglo')
        especificaciones = data.get("especificaciones", {})
        if not isinstance(especificaciones, dict):
            return jsonify({"error": "El campo 'especificaciones' debe ser un objeto JSON"}), 400

        # Crear el producto
        producto = {
            "nombre": data["nombre"],
            "tipo": data["tipo"],
            "precio": precio,
            "especificaciones": especificaciones,
            "stock": stock
        }

        result = mongo.db.productos.insert_one(producto)

        return jsonify({"message": "Producto agregado", "id": str(result.inserted_id)}), 201

    except Exception as e:
        print(f"❌ Error al agregar producto: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Editar un producto
@admin_prod_bp.route('/admin/productos/<id>', methods=['PUT'])
@admin_required
def editar_producto(id):
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400

        if not ObjectId.is_valid(id):
            return jsonify({"error": "ID no válido"}), 400

        producto = mongo.db.productos.find_one({"_id": ObjectId(id)})
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        # Excluir el campo '_id' para evitar error de MongoDB
        update_data = {k: v for k, v in data.items() if k != "_id" and v is not None}

        mongo.db.productos.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        response = jsonify({"message": "Producto actualizado"})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response, 200

    except Exception as e:
        print(f"❌ Error al actualizar producto: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Eliminar un producto
@admin_prod_bp.route('/admin/productos/<id>', methods=['DELETE'])
@admin_required
def eliminar_producto(id):
    result = mongo.db.productos.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Producto eliminado"}), 200
    return jsonify({"error": "Producto no encontrado"}), 404
