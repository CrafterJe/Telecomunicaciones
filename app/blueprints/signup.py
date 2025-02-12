from flask import Blueprint, request, jsonify
from app.config import create_app
from app.config.extensions import mongo
import bcrypt
from jwt import encode, decode  # Importación para JWT
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mi_clave_secreta_default')

# Crear el Blueprint para la autenticación
auth = Blueprint('auth', __name__)
app = create_app()

@auth.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validar los campos requeridos
        required_fields = ['nombre', 'usuario', 'email', 'password']
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"error": "Todos los campos son obligatorios"}), 400

        # Verificar si el nombre de usuario ya existe
        existing_user = mongo.db.usuarios.find_one({"usuario": data['usuario']})
        if existing_user:
            return jsonify({"error": "El nombre de usuario ya está registrado"}), 400

        # Encriptar la contraseña usando bcrypt
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

        # Crear el nuevo usuario con rol por defecto "usuario"
        new_user = {
            "nombre": data['nombre'],
            "usuario": data['usuario'],
            "email": data['email'],
            "password": hashed_password.decode('utf-8'),
            "rol": "usuario",  # Se asigna el rol por defecto
            "fecha_registro": datetime.utcnow()
        }

        # Insertar el nuevo usuario en la base de datos y obtener su ID
        result = mongo.db.usuarios.insert_one(new_user)
        new_user_id = result.inserted_id

        # Crear el carrito vacío para el usuario
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

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('usuario')
        password = data.get('password')

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

            # Verificar si existe el carrito
            carrito = mongo.db.carrito.find_one({"usuario_id": usuario["_id"]})
            if not carrito:
                # Si no existe el carrito, crearlo por consistencia
                mongo.db.carrito.insert_one({
                    "usuario_id": usuario["_id"],
                    "productos": [],
                    "total": 0,
                    "fecha_creacion": datetime.utcnow()
                })

            # Convertir token a string si es bytes
            if isinstance(token, bytes):
                token = token.decode('utf-8')

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
