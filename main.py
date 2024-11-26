from app import create_app
from app.blueprints.productos import prod
from app.blueprints.usuarios import usrs
from app.blueprints.pagos import pays
from app.blueprints.creditos import creds
from app.blueprints.transacciones import tran
from flask_cors import CORS

app = create_app()

app.register_blueprint(prod)
app.register_blueprint(usrs)
app.register_blueprint(pays)
app.register_blueprint(creds)
app.register_blueprint(tran)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=4000, debug=True)