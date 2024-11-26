from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

prod = Blueprint('users', __name__)
app = create_app()

@prod.route('/usuarios/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.usuarios.find({})
    r=[]
    for usuario in data:
        usuario['_id'] = str(usuario['_id'])
        r.append(usuario)
    v = dumps(r)
    return v


@prod.route('/usuarios/create', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    result = mongo.db.usuarios.insert_one(data)
    return jsonify({"msg": "Usuario creado", "id": str(result.inserted_id)})


@prod.route('/usuarios/update/<id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.get_json()
    result = mongo.db.usuarios.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Usuario actualizado"})
    else:
        return jsonify({"msg": "Usuario no encontrado"}), 404


@prod.route('/usuarios/delete/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    result = mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Usuario eliminado"})
    else:
        return jsonify({"msg": "Usuario no encontrado"}), 404
