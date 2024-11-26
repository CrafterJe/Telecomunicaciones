from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

prod = Blueprint('credits', __name__)
app = create_app()

@prod.route('/creditos/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.creditos.find({})
    r=[]
    for credito in data:
        credito['_id'] = str(credito['_id'])
        r.append(credito)
    v = dumps(r)
    return v

@prod.route('/creditos/create', methods=['POST'])
def crear_credito():
    data = request.get_json()
    result = mongo.db.creditos.insert_one(data)
    return jsonify({"msg": "Crédito creado", "id": str(result.inserted_id)})


@prod.route('/creditos/update/<id>', methods=['PUT'])
def actualizar_credito(id):
    data = request.get_json()
    result = mongo.db.creditos.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Crédito actualizado"})
    else:
        return jsonify({"msg": "Crédito no encontrado"}), 404


@prod.route('/creditos/delete/<id>', methods=['DELETE'])
def eliminar_credito(id):
    result = mongo.db.creditos.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Crédito eliminado"})
    else:
        return jsonify({"msg": "Crédito no encontrado"}), 404
