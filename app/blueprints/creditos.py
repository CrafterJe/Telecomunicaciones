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