from flask import Blueprint, jsonify, request
from app.config.extensions import mongo
from bson import ObjectId
import jwt
from functools import wraps
from app.blueprints.config import SECRET_KEY

admin_bp = Blueprint('admin', __name__)

# Middleware para verificar si el usuario es admin
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

# 🔥 Obtener total de usuarios (solo admins)
@admin_bp.route('/admin/usuarios/total', methods=['GET'])
@admin_required
def total_usuarios():
    total = mongo.db.usuarios.count_documents({})
    return jsonify({"total": total})

# 🔥 Obtener total de productos en stock (solo admins)
@admin_bp.route('/admin/productos/total', methods=['GET'])
@admin_required
def total_productos():
    total = mongo.db.productos.count_documents({})
    return jsonify({"total": total})

# 🔥 Obtener lista de usuarios (solo admins)
@admin_bp.route('/admin/usuarios', methods=['GET'])
@admin_required
def obtener_usuarios():
    usuarios = list(mongo.db.usuarios.find({}, {"password": 0}))  # No enviar contraseñas
    for usuario in usuarios:
        usuario["_id"] = str(usuario["_id"])
    return jsonify(usuarios)

# 🔥 Eliminar usuario por ID (solo admins)
@admin_bp.route('/admin/usuarios/<id>', methods=['DELETE'])
@admin_required
def eliminar_usuario(id):
    token = request.headers.get('Authorization')
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token.get("user_id")

    # Evitar que un admin se elimine a sí mismo
    if id == user_id:
        return jsonify({"error": "No puedes eliminar tu propio usuario"}), 403

    result = mongo.db.usuarios.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Usuario eliminado"}), 200
    return jsonify({"error": "Usuario no encontrado"}), 404

@admin_bp.route('/admin/usuarios/<id>/rol', methods=['PUT'])
@admin_required
def actualizar_rol(id):
    data = request.json
    print(f"🔹 Datos recibidos para actualizar rol: {data}")  # 🔥 Ver qué datos llegan

    nuevo_rol = data.get("rol")

    if nuevo_rol not in ["usuario", "admin"]:
        print("❌ Error: Rol inválido")
        return jsonify({"error": "Rol inválido"}), 400

    token = request.headers.get('Authorization')
    token = token.replace("Bearer ", "").strip()
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    user_id = decoded_token.get("user_id")

    # 🔥 Evitar que un admin se degrade a usuario
    if id == user_id and nuevo_rol == "usuario":
        print("❌ Intento de degradarse a usuario")
        return jsonify({"error": "No puedes cambiarte tu propio rol a usuario"}), 403

    result = mongo.db.usuarios.update_one({"_id": ObjectId(id)}, {"$set": {"rol": nuevo_rol}})

    if result.matched_count:
        print("✅ Rol actualizado correctamente")
        return jsonify({"message": "Rol actualizado"}), 200

    print("❌ Usuario no encontrado")
    return jsonify({"error": "Usuario no encontrado"}), 404

