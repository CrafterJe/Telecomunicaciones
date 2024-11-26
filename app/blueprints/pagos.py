from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

prod = Blueprint('pays', __name__)
app = create_app()

@prod.route('/pagos/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.pagos.find({})
    r=[]
    for pago in data:
        pago['_id'] = str(pago['_id'])
        r.append(pago)
    v = dumps(r)
    return v

@prod.route('/pagos/create', methods=['POST'])
def crear_pago():
    data = request.get_json()
    result = mongo.db.pagos.insert_one(data)
    return jsonify({"msg": "Pago creado", "id": str(result.inserted_id)})


@prod.route('/pagos/update/<id>', methods=['PUT'])
def actualizar_pago(id):
    data = request.get_json()
    result = mongo.db.pagos.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Pago actualizado"})
    else:
        return jsonify({"msg": "Pago no encontrado"}), 404


@prod.route('/pagos/delete/<id>', methods=['DELETE'])
def eliminar_pago(id):
    result = mongo.db.pagos.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Pago eliminado"})
    else:
        return jsonify({"msg": "Pago no encontrado"}), 404
