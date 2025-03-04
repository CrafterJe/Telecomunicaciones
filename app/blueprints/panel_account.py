from flask import Blueprint, request, jsonify
from app.config.extensions import mongo
import bcrypt
from bson import ObjectId
from app.blueprints.decorators import auth_required

panel_acc = Blueprint('panel_account', __name__)

# OBTENER PERFIL DEL USUARIO
@panel_acc.route('/get-profile', methods=['GET'])
@auth_required
def get_profile():
    try:
        usuario_actual = request.usuario  # Usuario autenticado

        # Excluir la contraseña por seguridad
        user_data = {
            "nombre": usuario_actual.get("nombre", ""),
            "apellidoP": usuario_actual.get("apellidoP", ""),
            "apellidoM": usuario_actual.get("apellidoM", ""),
            "usuario": usuario_actual.get("usuario", ""),
            "email": usuario_actual.get("email", "")
        }

        return jsonify(user_data), 200

    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500

# ACTUALIZAR NOMBRE Y APELLIDOS
@panel_acc.route('/update-profile/nombre', methods=['PUT'])
@auth_required
def update_nombre():
    try:
        data = request.get_json()
        usuario_actual = request.usuario  

        update_fields = {}
        if "nombre" in data:
            update_fields["nombre"] = data["nombre"]
        if "apellidoP" in data:
            update_fields["apellidoP"] = data["apellidoP"]
        if "apellidoM" in data:
            update_fields["apellidoM"] = data["apellidoM"]

        mongo.db.usuarios.update_one({"_id": usuario_actual["_id"]}, {"$set": update_fields})
        return jsonify({"message": "Nombre actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500


# ACTUALIZAR USUARIO
@panel_acc.route('/update-profile/usuario', methods=['PUT'])
@auth_required
def update_usuario():
    try:
        data = request.get_json()
        usuario_actual = request.usuario  

        if "usuario" in data:
            existing_user = mongo.db.usuarios.find_one({"usuario": data["usuario"], "_id": {"$ne": usuario_actual["_id"]}})
            if existing_user:
                return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

            mongo.db.usuarios.update_one({"_id": usuario_actual["_id"]}, {"$set": {"usuario": data["usuario"]}})
            return jsonify({"message": "Usuario actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500


# ACTUALIZAR EMAIL
@panel_acc.route('/update-profile/email', methods=['PUT'])
@auth_required
def update_email():
    try:
        data = request.get_json()
        usuario_actual = request.usuario  

        if "email" in data:
            existing_email = mongo.db.usuarios.find_one({"email": data["email"], "_id": {"$ne": usuario_actual["_id"]}})
            if existing_email:
                return jsonify({"error": "El email ya está en uso"}), 400

            mongo.db.usuarios.update_one({"_id": usuario_actual["_id"]}, {"$set": {"email": data["email"]}})
            return jsonify({"message": "Email actualizado exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500


# ACTUALIZAR CONTRASEÑA (verificando la actual)
@panel_acc.route('/update-profile/password', methods=['PUT'])
@auth_required
def update_password():
    try:
        data = request.get_json()
        usuario_actual = request.usuario  

        current_password = data.get("current_password")
        new_password = data.get("new_password")

        if not current_password or not new_password:
            return jsonify({"error": "Debe proporcionar la contraseña actual y la nueva"}), 400

        # Verificar la contraseña actual
        if not bcrypt.checkpw(current_password.encode('utf-8'), usuario_actual["password"].encode('utf-8')):
            return jsonify({"error": "La contraseña actual es incorrecta"}), 400

        # Encriptar la nueva contraseña
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        mongo.db.usuarios.update_one({"_id": usuario_actual["_id"]}, {"$set": {"password": hashed_password}})
        return jsonify({"message": "Contraseña actualizada exitosamente"}), 200

    except Exception as e:
        return jsonify({"error": "Error en el servidor"}), 500
