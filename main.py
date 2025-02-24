from app.config import create_app
from app.blueprints.admin import admin_bp
from app.blueprints.admin import admin_prod_bp
from app.blueprints.productos import prod
from app.blueprints.usuarios import usrs
from app.blueprints.pagos import pays
from app.blueprints.creditos import creds
from app.blueprints.transacciones import tran
from app.blueprints.carrito import cart
from app.blueprints.auth import auth
from flask_cors import CORS

app = create_app()

CORS(app, resources={r"/*": {
    "origins": ["http://localhost:4200", "http://192.168.100.15:4200","*"],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization", "Accept"]
}})

# Registrar los blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(admin_prod_bp)
app.register_blueprint(prod)
app.register_blueprint(usrs)
app.register_blueprint(pays)
app.register_blueprint(creds)
app.register_blueprint(tran)
app.register_blueprint(cart, url_prefix='/carrito')
app.register_blueprint(auth)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
