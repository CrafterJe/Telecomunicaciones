from datetime import datetime
from bson import ObjectId
from app.config import create_app
from app.config.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

usrs = Blueprint('users', __name__)

@usrs.route('/usuarios/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.usuarios.find({})
    r=[]
    for usuario in data:
        usuario['_id'] = str(usuario['_id'])
        r.append(usuario)
    v = dumps(r)
    return v


@usrs.route('/usuarios/create', methods=['POST'])
def crear_usuario():
    data = request.get_json()
    result = mongo.db.usuarios.insert_one(data)
    return jsonify({"msg": "Usuario creado", "id": str(result.inserted_id)})


@usrs.route('/usuarios/update/<id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.get_json()
    result = mongo.db.usuarios.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Usuario actualizado"})
    else:
        return jsonify({"msg": "Usuario no encontrado"}), 404


@usrs.route('/usuarios/delete/<id>', methods=['DELETE'])
def eliminar_usuario(id):
    result = mongo.db.usuarios.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Usuario eliminado"})
    else:
        return jsonify({"msg": "Usuario no encontrado"}), 404
