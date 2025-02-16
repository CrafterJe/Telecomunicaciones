from datetime import datetime
from bson import ObjectId
from app.config import create_app
from app.config.extensions import mongo
from flask import Blueprint, jsonify
from bson.json_util import dumps
from flask import request

prod = Blueprint('products', __name__)
app = create_app()

@prod.route('/productos/get_all', methods=['GET'])
def listar_prod():
    data=mongo.db.productos.find({})
    r=[]
    for producto in data:
        producto['_id'] = str(producto['_id'])
        r.append(producto)
    v = dumps(r)
    return v
