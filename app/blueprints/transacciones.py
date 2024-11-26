from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

prod = Blueprint('transactions', __name__)
app = create_app()

@prod.route('/transacciones/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.transacciones.find({})
    r=[]
    for transaccion in data:
        transaccion['_id'] = str(transaccion['_id'])
        r.append(transaccion)
    v = dumps(r)
    return v