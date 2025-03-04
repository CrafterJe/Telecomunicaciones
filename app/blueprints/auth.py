from flask import Blueprint, request, jsonify
from app.config import create_app
from app.config.extensions import mongo
import bcrypt
from jwt import encode, decode  # Importación para JWT
from datetime import datetime, timedelta
import os
from app.blueprints.config import SECRET_KEY, RECAPTCHA_SECRET_KEY
import jwt
from bson import ObjectId
import requests

# Crear el Blueprint para la autenticación
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        required_fields = ['nombre', 'apellidoP', 'usuario', 'email', 'password']  # Quitamos apellidoM de los requeridos
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"error": "Todos los campos obligatorios deben estar llenos"}), 400

        existing_user = mongo.db.usuarios.find_one({"usuario": data['usuario']})
        if existing_user:
            return jsonify({"error": "El nombre de usuario ya está registrado"}), 400

        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        new_user = {
            "nombre": data['nombre'],
            "apellidoP": data['apellidoP'],
            "apellidoM": data.get('apellidoM', ''),  # Si no se envía, se asigna una cadena vacía
            "usuario": data['usuario'],
            "email": data['email'],
            "password": hashed_password.decode('utf-8'),
            "rol": "usuario",
            "fecha_registro": datetime.utcnow()
        }

        result = mongo.db.usuarios.insert_one(new_user)
        new_user_id = result.inserted_id

        mongo.db.carrito.insert_one({
            "usuario_id": new_user_id,
            "productos": [],
            "total": 0,
            "fecha_creacion": datetime.utcnow()
        })

        return jsonify({"message": "Usuario registrado exitosamente"}), 201

    except Exception as e:
        print("Error en register:", str(e))
        return jsonify({"error": "Error en el servidor"}), 500


USE_RECAPTCHA = True
@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('usuario')
        password = data.get('password')
        captcha_token = data.get('captcha')  # Captura el token de reCAPTCHA

        # Verificar reCAPTCHA solo si está activado
        if USE_RECAPTCHA:
            captcha_verify_url = "https://www.google.com/recaptcha/api/siteverify"
            response = requests.post(captcha_verify_url, data={
                "secret": RECAPTCHA_SECRET_KEY,
                "response": captcha_token
            })
            captcha_result = response.json()

            if not captcha_result.get("success"):
                return jsonify({"message": "Captcha inválido"}), 400

        # Validar campos requeridos
        if not username or not password:
            return jsonify({"message": "Usuario y contraseña son obligatorios"}), 400

        # Buscar al usuario en la base de datos
        usuario = mongo.db.usuarios.find_one({"usuario": username})

        if not usuario:
            return jsonify({"message": "Usuario no encontrado"}), 404

        # Verificar la contraseña
        if bcrypt.checkpw(password.encode('utf-8'), usuario['password'].encode('utf-8')):

            # Obtener el rol del usuario (por defecto "usuario" si no existe)
            rol = usuario.get("rol", "usuario")

            # Generar un token JWT que incluya el rol
            token = encode(
                {
                    'user_id': str(usuario['_id']),
                    'nombre': usuario['nombre'],
                    'rol': rol,  # Incluir el rol en el token
                    'exp': datetime.utcnow() + timedelta(hours=1)
                },
                SECRET_KEY,
                algorithm='HS256'
            )

            return jsonify({
                'token': token,
                'user_id': str(usuario['_id']),
                'username': usuario['nombre'],
                'rol': rol,  # Se devuelve el rol en la respuesta
                'message': 'Login exitoso'
            }), 200

        return jsonify({"message": "Contraseña incorrecta"}), 401

    except Exception as e:
        print("Error en login:", str(e))
        return jsonify({"message": "Error en el servidor"}), 500


@auth.route('/auth/rol', methods=['GET'])
def obtener_rol():
    token = request.headers.get('Authorization')

    if not token:
        return jsonify({"error": "Acceso no autorizado"}), 403

    try:
        token = token.replace("Bearer ", "").strip()
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded_token.get("user_id")

        usuario = mongo.db.usuarios.find_one({"_id": ObjectId(user_id)})
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return jsonify({"rol": usuario.get("rol", "usuario")}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 403
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 403
