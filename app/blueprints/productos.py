from datetime import datetime
from bson import ObjectId
from app import create_app
from app.extensions import mongo
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


@prod.route('/productos/create', methods=['POST'])
def crear_producto():
    data = request.get_json()
    result = mongo.db.productos.insert_one(data)
    return jsonify({"msg": "Producto creado", "id": str(result.inserted_id)})


@prod.route('/productos/update/<id>', methods=['PUT'])
def actualizar_producto(id):
    data = request.get_json()
    result = mongo.db.productos.update_one({'_id': ObjectId(id)}, {'$set': data})
    if result.matched_count > 0:
        return jsonify({"msg": "Producto actualizado"})
    else:
        return jsonify({"msg": "Producto no encontrado"}), 404


@prod.route('/productos/delete/<id>', methods=['DELETE'])
def eliminar_producto(id):
    result = mongo.db.productos.delete_one({'_id': ObjectId(id)})
    if result.deleted_count > 0:
        return jsonify({"msg": "Producto eliminado"})
    else:
        return jsonify({"msg": "Producto no encontrado"}), 404





#@prod.route('/productos/porNombre/<string:nombre>', methods=['GET'])
#def obtener_PorNombre(nombre):
#    query = {'nombre':{'$eq':nombre}}
#    sort = [("nombre",1)]
#    project = {"_id":0,"clave":1,"nombre":1,"precio":1}
#    try:
#        resultado = mongo.db.productos.find(query, project).sort(sort)
#        if resultado:
#            return dumps(resultado)
#        else:
#            return dumps({"mensaje":"Documento no encontrado"}),404
#        
#    except Exception as e:
#        return dumps({"mensaje":str(e)}),500
#    
#@prod.route('/productos/porID/<string:id>', methods=['GET'])
#def obtener_porID(id):
#    query = {'_id':ObjectId(id)}
#    project = {"_id":0,"clave":1,"nombre":1,"costo":1,"precio":1,"status":1}
#    try:
#        resultado = mongo.db.productos.find_one(query, project)
#        if resultado:
#            return dumps(resultado)
#        else:
#            return dumps({"mensaje":"Documento no encontrado"}),404
#        
#    except Exception as e:
#        return dumps({"mensaje":str(e)}),500
#    
#@prod.route('/productos/nuevoProd',methods=['POST'])
#def add_producto():
#    clave = request.json["clave"]
#    nombre = request.json["nombre"]
#    marca = request.json["marca"]
#
#    alto = request.json["medidas"]["alto"]
#    ancho = request.json["medidas"]["ancho"]
#    grosor = request.json["medidas"]["grosor"]
#    peso = request.json["peso"]
#    modelo = request.json["modelo"]
#    costo = request.json["costo"]
#    cantidad_existente = request.json["cantidad_existente"]
#    status = request.json["status"]
#    sistema_operativo = request.json["sistema_operativo"]
#    velocidad_procesador = request.json["velocidad_procesador"]
#    resolucion_pantalla = request.json["resolucion_pantalla"]
#    tipo_bateria = request.json["tipo_bateria"]
#    memoria_interna = request.json["memoria_interna"]
#    codec_audio = request.json["codec_audio"]
#    cpu = request.json["CPU"]
#    camara = request.json["camara"]
#    memoria_ram = request.json["memoria_RAM"]
#    conexiones = request.json["conexiones"]
#    fecha_str = request.json["fecha_adquisicion"]
#    fechaAdq = datetime.strptime(fecha_str, "%Y-%m-%d")
#
#    origen = request.json["origen"]
#    foto = request.json["foto"]
#    proveedorid_str = request.json["proveedorId"]
#    proveedorId = ObjectId(proveedorid_str)
#    caracteristicas_destacadas = request.json["caracteristicas_destacadas"]
#    
#    
#    if request.method == "POST":
#        product = {
#
#            "clave": clave,
#            "nombre": nombre,
#            "marca": marca,
#            "medidas":{"alto":alto, "ancho":ancho, "grosor":grosor},
#            "peso": peso,
#            "modelo": modelo,
#            "costo": costo,
#            "precio": costo+costo*20/100,
#            "cantidad_existente": cantidad_existente,
#            "status": status,
#            "sistema_operativo": sistema_operativo,
#            "velocidad_procesador": velocidad_procesador,
#            "resolucion_pantalla": resolucion_pantalla,
#            "tipo_bateria": tipo_bateria,
#            "memoria_interna": memoria_interna,
#            "codec_audio": codec_audio,
#            "CPU": cpu,
#            "camara": camara,
#            "memoria_RAM": memoria_ram,
#            "conexiones": conexiones,
#            "fecha_adquisicion": fechaAdq,
#            "origen": origen,
#            "foto": foto,
#            "proveedorId": proveedorId,
#            "caracteristicas_destacadas": caracteristicas_destacadas
#            }
#    try:
#        resultado = mongo.db.productos.insert_one(product)
#        if resultado:
#            return jsonify({"mensaje":"Documento Insertado"})
#        else:
#            return jsonify({"mensaje":"Documento no Insertado"}),404
#    except Exception as e:
#        return jsonify({"error":str(e)}),500
#    
#@prod.route('/productos/eliminar/<string:id>',methods=['DELETE'])
#def eliminar(id):
#    try:
#        resultado = mongo.db.productos.delete_one({'_id':ObjectId(id)})
#        if resultado:
#            return jsonify({"mensaje":"Documento Eliminado"})
#        else:
#            return jsonify({"mensaje":"Documento no Encontrado"}),404
#    except Exception as e:
#        return jsonify({"error":str(e)}),500
#
#@prod.route('/productos/prod_prov',methods=['GET'])
#def obtener_prod_prov():
#    query = [
#        {
#            "$lookup": {
#                "from": "proveedores",
#                "localField": "proveedorId",
#                "foreignField": "_id",
#                "as": "proveedor"
#            }
#        },
#        {
#            '$unwind' : "$proveedor"
#        },
#        {
#            '$project':{
#                "_id":0,
#                "clave":1,
#                "nombre":1,
#                "proveedor.nombre":1
#            }
#        }
#    ]
#    try:
#        resultado = mongo.db.productos.aggregate(query)
#        if resultado:
#            return list(resultado)
#        else:
#            return jsonify({"mensaje":"Documento no encontrado"}),404
#    except Exception as e:
#        return jsonify({"error":str(e)}),500
#    
#@prod.route('/productos/actualizar/<string:id>',methods=['PUT'])
#def actualizar_costo(id):
#    nuevo_costo = request.json["costo"]
#    nuevo_nombre = request.json.get("nombre")
#    nueva_clave = request.json.get("clave")
#    nuevo_status = request.json.get("status")
#
#    try:
#        if nuevo_costo is not None:
#            resultado = mongo.db.productos.update_one({'_id': ObjectId(id)}, {"$set": {"costo": nuevo_costo}})
#            if resultado:
#                actualizar_precio(id, nuevo_costo)
#            else:
#                return jsonify({"mensaje": "Documento no Actualizado"}), 404
#        
#        if nuevo_nombre is not None:
#            resultado = mongo.db.productos.update_one({'_id': ObjectId(id)}, {"$set": {"nombre": nuevo_nombre}})
#            if not resultado:
#                return jsonify({"mensaje": "Documento no Actualizado"}), 404
#
#        if nueva_clave is not None:
#            resultado = mongo.db.productos.update_one({'_id': ObjectId(id)}, {"$set": {"clave": nueva_clave}})
#            if not resultado:
#                return jsonify({"mensaje": "Documento no Actualizado"}), 404
#
#        if nuevo_status is not None:
#            resultado = mongo.db.productos.update_one({'_id': ObjectId(id)}, {"$set": {"status": nuevo_status}})
#            if not resultado:
#                return jsonify({"mensaje": "Documento no Actualizado"}), 404
#
#        return jsonify({"mensaje": "Documento Actualizado"})
#    except Exception as e:
#        return jsonify({"error": str(e)}), 500
#def actualizar_precio(id,nuevo_costo):
#    try:
#        resultado = mongo.db.productos.update_one({'_id':ObjectId(id)},{"$set":{"precio":nuevo_costo+(nuevo_costo*20/100)}})
#        if resultado:
#            return jsonify({"mensaje":"Documento Actualizado"})
#        else:
#            return jsonify({"mensaje":"Documento no Encontrado"}),404
#    except Exception as e:
#        return jsonify({"error":str(e)}),500