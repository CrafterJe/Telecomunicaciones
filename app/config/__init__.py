from flask import Flask
from app.config.config import MONGO_URI
from app.config.extensions import mongo
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config['MONGO_URI'] = MONGO_URI
    mongo.init_app(app)

    CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:4200", "http://192.168.100.33:4200", "*"],  # URL de Angular
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"]
    }
})
    return app