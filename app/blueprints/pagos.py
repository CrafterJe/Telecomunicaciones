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