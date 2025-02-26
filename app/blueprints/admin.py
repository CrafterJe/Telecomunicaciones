from flask import Blueprint, jsonify, request
from app.config.extensions import mongo
from bson import ObjectId
import jwt
from functools import wraps
from app.blueprints.config import SECRET_KEY
import base64

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
@admin_bp.route('/usuarios/total', methods=['GET'])
@admin_required
def total_usuarios():
    total = mongo.db.usuarios.count_documents({})
    return jsonify({"total": total})

# Obtener total de productos en stock (solo admins)
@admin_bp.route('/productos/total', methods=['GET'])
@admin_required
def total_productos():
    total = mongo.db.productos.count_documents({})
    return jsonify({"total": total})

# Obtener lista de usuarios (solo admins)
@admin_bp.route('/usuarios', methods=['GET'])
@admin_required
def obtener_usuarios():
    usuarios = list(mongo.db.usuarios.find({}, {"password": 0}))  # No enviar contraseñas
    for usuario in usuarios:
        usuario["_id"] = str(usuario["_id"])
    return jsonify(usuarios)

# Eliminar usuario por ID (solo admins)
@admin_bp.route('/usuarios/<id>', methods=['DELETE'])
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


@admin_bp.route('/usuarios/<id>/rol', methods=['PUT'])
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

@admin_prod_bp.route('/productos', methods=['GET'])
@admin_required
def obtener_productos():
    try:
        productos = list(mongo.db.productos.find({}))

        for producto in productos:
            producto["_id"] = str(producto["_id"])

            # Convertir las imágenes a base64 si existen
            if "imagenes" in producto:
                imagenes = producto.get("imagenes")
                imagenes_convertidas = []

                for imagen in imagenes:
                    if isinstance(imagen, dict) and "$binary" in imagen:
                        imagenes_convertidas.append(imagen["$binary"]["base64"])
                
                producto["imagenes"] = imagenes_convertidas

        return jsonify(productos), 200

    except Exception as e:
        print(f"❌ Error al obtener productos: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

    
# Agregar un nuevo producto
@admin_prod_bp.route('/productos', methods=['POST'])
def agregar_producto():
    try:
        data = request.form.to_dict()  # Capturar los datos desde el formulario
        imagenes = request.files.getlist('imagenes')  # Capturar múltiples imágenes

        # 🔍 Validar campos requeridos
        if not data.get("nombre") or not data.get("tipo") or "precio" not in data:
            return jsonify({"error": "Faltan datos requeridos (nombre, tipo, precio)"}), 400

        # 🔢 Validar que precio y stock sean números positivos
        try:
            precio = float(data["precio"])
            stock = int(data.get("stock", 0))

            if precio < 0 or stock < 0:
                return jsonify({"error": "El precio y el stock deben ser números positivos"}), 400
        except ValueError:
            return jsonify({"error": "El precio debe ser un número válido y el stock un número entero"}), 400

        # 📝 Validar que las especificaciones sean un diccionario JSON
        especificaciones = data.get("especificaciones", "{}")
        try:
            especificaciones = json.loads(especificaciones)
        except json.JSONDecodeError:
            return jsonify({"error": "Formato de especificaciones inválido, debe ser un objeto JSON"}), 400

        # 📸 Procesar imágenes (máximo 5)
        imagenes_guardadas = []
        if not imagenes:
            return jsonify({"error": "Debe subir al menos una imagen del producto"}), 400

        for imagen in imagenes[:5]:  # Limitar a 5 imágenes
            if imagen and imagen.filename.lower().endswith(('.jpg', '.jpeg')):
                encoded_image = base64.b64encode(imagen.read()).decode('utf-8')
                imagenes_guardadas.append({
                    "$binary": {
                        "base64": encoded_image,
                        "subType": "00"
                    }
                })
            else:
                return jsonify({"error": "Las imágenes deben estar en formato JPG o JPEG"}), 400

        # 🎥 Validar y agregar enlace de video si existe
        video_link = data.get('videoLink')
        if video_link and "youtube.com/watch?v=" not in video_link:
            return jsonify({"error": "El enlace del video debe ser un enlace válido de YouTube"}), 400

        # ✅ Crear el producto
        producto = {
            "nombre": data["nombre"],
            "tipo": data["tipo"],
            "precio": precio,
            "especificaciones": especificaciones,
            "stock": stock,
            "imagenes": imagenes_guardadas,
            "videoLink": video_link
        }

        # 💾 Insertar el producto en la base de datos
        result = mongo.db.productos.insert_one(producto)

        return jsonify({"message": "Producto agregado correctamente", "id": str(result.inserted_id)}), 201

    except Exception as e:
        print(f"❌ Error al agregar producto: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

# Editar un producto
import json 

@admin_prod_bp.route('/productos/<id>', methods=['PUT'])
@admin_required
def editar_producto(id):
    try:
        data = request.form.to_dict()
        imagenes_nuevas = request.files.getlist('imagenes')

        if not ObjectId.is_valid(id):
            return jsonify({"error": "ID no válido"}), 400

        producto = mongo.db.productos.find_one({"_id": ObjectId(id)})
        if not producto:
            return jsonify({"error": "Producto no encontrado"}), 404

        update_data = {k: v for k, v in data.items() if k != "_id" and v is not None}

        # ✅ Convertir y validar especificaciones si existen
        if "especificaciones" in update_data:
            try:
                update_data["especificaciones"] = json.loads(update_data["especificaciones"])
            except json.JSONDecodeError:
                return jsonify({"error": "Formato de especificaciones inválido"}), 400

        # ✅ Convertir y validar precio
        if "precio" in update_data:
            try:
                update_data["precio"] = float(update_data["precio"])
                if update_data["precio"] <= 0:
                    return jsonify({"error": "El precio debe ser un número mayor a 0."}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "El precio debe ser un número válido."}), 400

        # ✅ Convertir y validar stock
        if "stock" in update_data:
            try:
                update_data["stock"] = int(update_data["stock"])
                if update_data["stock"] < 0:
                    return jsonify({"error": "El stock debe ser un número entero mayor o igual a 0."}), 400
            except (ValueError, TypeError):
                return jsonify({"error": "El stock debe ser un número entero válido."}), 400

        # ✅ Validar y actualizar `videoLink`
        if "videoLink" in data:
            update_data["videoLink"] = data["videoLink"]

        # 🗑️ Manejo de eliminación de imágenes si `removedImagesIndexes` existe
        if "removedImagesIndexes" in update_data:
            try:
                removed_indexes = json.loads(update_data["removedImagesIndexes"])
                if isinstance(removed_indexes, list) and removed_indexes:
                    removed_indexes.sort(reverse=True)
                    imagenes_actuales = producto.get("imagenes", [])

                    for index in removed_indexes:
                        if 0 <= index < len(imagenes_actuales):
                            del imagenes_actuales[index]

                    update_data["imagenes"] = imagenes_actuales
            except Exception as e:
                print(f"❌ Error al procesar removedImagesIndexes: {str(e)}")
                return jsonify({"error": "Error en removedImagesIndexes"}), 400

        # 🛠️ No guardar removedImagesIndexes en la BD
        update_data.pop("removedImagesIndexes", None)

        # ✅ Actualizar el producto en MongoDB
        mongo.db.productos.update_one({"_id": ObjectId(id)}, {"$set": update_data})

        return jsonify({"message": "Producto actualizado correctamente"}), 200

    except Exception as e:
        print(f"❌ Error al actualizar producto: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500


# Eliminar un producto
@admin_prod_bp.route('/productos/<id>', methods=['DELETE'])
@admin_required
def eliminar_producto(id):
    result = mongo.db.productos.delete_one({"_id": ObjectId(id)})
    if result.deleted_count:
        return jsonify({"message": "Producto eliminado"}), 200
    return jsonify({"error": "Producto no encontrado"}), 404
