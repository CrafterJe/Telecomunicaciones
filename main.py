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
from app.blueprints.panel_account import panel_acc

app = create_app()  

# Registrar los blueprints
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(admin_prod_bp, url_prefix='/admin')
app.register_blueprint(auth)
app.register_blueprint(cart, url_prefix='/carrito')
app.register_blueprint(creds)
app.register_blueprint(pays)
app.register_blueprint(prod)
app.register_blueprint(tran)
app.register_blueprint(usrs)
app.register_blueprint(panel_acc, url_prefix='/panel_account')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
