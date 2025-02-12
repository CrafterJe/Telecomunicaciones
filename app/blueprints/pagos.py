from datetime import datetime
from bson import ObjectId
from app.config import create_app
from app.config.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

pays = Blueprint('pays', __name__)
app = create_app()

@pays.route('/pagos/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.pagos.find({})
    r=[]
    for pago in data:
        pago['_id'] = str(pago['_id'])
        r.append(pago)
    v = dumps(r)
    return v

@pays.route('/pagos/create', methods=['POST'])
def crear_pago():
    data = request.get_json()
    result = mongo.db.pagos.insert_one(data)
    return jsonify({"msg": "Pago creado", "id": str(result.inserted_id)})


@pays.route('/pagos/update/<id>', methods=['PUT'])
def actualizar_pago(id):
    data = request.get_json()
    result = mongo.db.pagos.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Pago actualizado"})
    else:
        return jsonify({"msg": "Pago no encontrado"}), 404


@pays.route('/pagos/delete/<id>', methods=['DELETE'])
def eliminar_pago(id):
    result = mongo.db.pagos.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Pago eliminado"})
    else:
        return jsonify({"msg": "Pago no encontrado"}), 404
