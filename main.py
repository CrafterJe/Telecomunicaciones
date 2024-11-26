from app import create_app
from app.blueprints.productos import prod
from flask_cors import CORS

app = create_app()

app.register_blueprint(prod)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=4000, debug=True)