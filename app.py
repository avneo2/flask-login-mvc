"""
LOGIN con Flask, organizado como MVC.

    app.py          → ARRANQUE: crea la aplicación y une las tres piezas
    modelo.py       → M (Modelo):      los datos y sus reglas
    templates/      → V (Vista):       lo que ve el usuario (HTML)
    controlador.py  → C (Controlador): recibe la petición y decide qué hacer

Ejecutar:  python app.py   y abrir  http://localhost:5000
"""

import os

from flask import Flask

from controlador import controlador
from modelo import db

app = Flask(__name__)

# La sesión de Flask se guarda en una cookie FIRMADA con esta clave (como session_start() en PHP).
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "clave-solo-para-clase")

# Sin DATABASE_URL se usa un archivo SQLite (no hace falta XAMPP).
# Con DATABASE_URL se usa MySQL, la misma base login_app de las prácticas PHP:
#     mysql+pymysql://root:@localhost/login_app
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///login.db")

db.init_app(app)                     # el Modelo se conecta a la app
app.register_blueprint(controlador)  # el Controlador registra sus rutas

with app.app_context():
    db.create_all()                  # crea la tabla si no existe (CREATE TABLE IF NOT EXISTS)

if __name__ == "__main__":
    puerto = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=puerto, debug=True)
