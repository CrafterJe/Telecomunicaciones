from flask import request, jsonify
from functools import wraps
import jwt
from bson import ObjectId
from app.blueprints.config import SECRET_KEY
from app.config.extensions import mongo

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skipear autenticacion para OPTIONS requests
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Acceso no autorizado, se requiere token"}), 403

        try:
            token = token.replace("Bearer ", "").strip()
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token.get("user_id")

            usuario = mongo.db.usuarios.find_one({"_id": ObjectId(user_id)})
            if not usuario:
                return jsonify({"error": "Usuario no encontrado"}), 403

            request.usuario = usuario  # Se almacena el usuario en request para su uso posterior

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expirado"}), 403
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 403
        except Exception as e:
            return jsonify({"error": f"Error al procesar token: {str(e)}"}), 403

        return f(*args, **kwargs)
    
    return decorated_function