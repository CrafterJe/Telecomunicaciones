from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

tran = Blueprint('transactions', __name__)
app = create_app()

@tran.route('/transacciones/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.transacciones.find({})
    r=[]
    for transaccion in data:
        transaccion['_id'] = str(transaccion['_id'])
        r.append(transaccion)
    v = dumps(r)
    return v

@tran.route('/transacciones/create', methods=['POST'])
def crear_transaccion():
    data = request.get_json()
    result = mongo.db.transacciones.insert_one(data)
    return jsonify({"msg": "Transacción creada", "id": str(result.inserted_id)})


@tran.route('/transacciones/update/<id>', methods=['PUT'])
def actualizar_transaccion(id):
    data = request.get_json()
    result = mongo.db.transacciones.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Transacción actualizada"})
    else:
        return jsonify({"msg": "Transacción no encontrada"}), 404


@tran.route('/transacciones/delete/<id>', methods=['DELETE'])
def eliminar_transaccion(id):
    result = mongo.db.transacciones.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Transacción eliminada"})
    else:
        return jsonify({"msg": "Transacción no encontrada"}), 404
