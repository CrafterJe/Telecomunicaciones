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