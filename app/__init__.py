from flask import Flask
from app.config import MONGO_URI
from app.extensions import mongo
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = MONGO_URI
    mongo.init_app(app)

    CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4200"],  # Tu URL de Angular
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
    return app
