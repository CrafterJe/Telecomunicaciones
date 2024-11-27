from flask import Blueprint, request, jsonify
from app import create_app
from app.extensions import mongo
import bcrypt
from jwt import encode, decode  # O usa esta importación específica
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'mi_clave_secreta_default')
# Crear el Blueprint para la autenticación
auth = Blueprint('auth', __name__)
app = create_app()

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    # Verificar que todos los campos requeridos estén presentes
    if not data.get('nombre') or not data.get('usuario') or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    # Verificar si el nombre de usuario ya está registrado
    existing_user = mongo.db.usuarios.find_one({"usuario": data['usuario']})
    if existing_user:
        return jsonify({"error": "El nombre de usuario ya está registrado"}), 400

    # Encriptar la contraseña usando bcrypt
    hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())

    # Crear el nuevo usuario
    new_user = {
        "nombre": data['nombre'],
        "usuario": data['usuario'],
        "email": data['email'],
        "password": hashed_password.decode('utf-8'),
        "tipo": "cliente",  # El tipo de usuario, puedes cambiarlo si es necesario
        "fecha_registro": datetime.utcnow()  # Fecha actual en formato UTC
    }

    # Insertar el nuevo usuario en la base de datos
    mongo.db.usuarios.insert_one(new_user)

    return jsonify({"message": "Usuario registrado exitosamente"}), 201

@auth.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('usuario')
        password = data.get('password')

        # Buscar al usuario en la base de datos
        usuario = mongo.db.usuarios.find_one({"usuario": username})
        
        if not usuario:
            return jsonify({"message": "Usuario no encontrado"}), 404

        # Verificar la contraseña
        if bcrypt.checkpw(password.encode('utf-8'), usuario['password'].encode('utf-8')):
            # Generar un token JWT
            token = encode(
                {
                    'user_id': str(usuario['_id']),
                    'exp': datetime.utcnow() + timedelta(hours=1)
                }, 
                SECRET_KEY, 
                algorithm='HS256'
            )

            # Si el token es bytes, convertirlo a string
            if isinstance(token, bytes):
                token = token.decode('utf-8')

            return jsonify({'token': token, 'message': 'Login exitoso'}), 200
        
        # Si la contraseña no coincide
        return jsonify({"message": "Contraseña incorrecta"}), 401

    except Exception as e:
        print("Error en login:", str(e))  # Para debugging
        return jsonify({"message": "Error en el servidor"}), 500