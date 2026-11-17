"""
M — MODELO: los datos y sus reglas.

Aquí NO hay HTML ni formularios ni redirecciones. Solo la clase Usuario,
que representa una fila de la tabla `usuarios` (la misma de LOGIN/database.sql).
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()

SEXOS = ["Hombre", "Mujer", "Otro"]


class Usuario(db.Model):
    __tablename__ = "usuarios"

    # Cada atributo es una columna. Compara con LOGIN/database.sql.
    id            = db.Column(db.Integer, primary_key=True)
    nombre        = db.Column(db.String(100), nullable=False)
    correo        = db.Column(db.String(150), nullable=False, unique=True)
    sexo          = db.Column(db.String(10), nullable=False)
    edad          = db.Column(db.Integer, nullable=False)
    carrera       = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    creado_en     = db.Column(db.DateTime, server_default=db.func.now())

    # ---------- Reglas del negocio: viven en el Modelo, no en el Controlador ----------

    @classmethod
    def registrar(cls, nombre, correo, sexo, edad, carrera, password, confirmar):
        """Valida los datos y crea el usuario. Si algo está mal, lanza ValueError con el motivo."""
        nombre, correo, carrera = nombre.strip(), correo.strip(), carrera.strip()
        edad = int(edad) if edad.isdigit() else 0

        if not nombre or not carrera or "@" not in correo or sexo not in SEXOS or not 15 <= edad <= 99:
            raise ValueError("Revisa que todos los datos sean válidos.")
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if password != confirmar:
            raise ValueError("Las contraseñas no coinciden.")
        if cls.query.filter_by(correo=correo).first():
            raise ValueError("Ese correo ya está registrado.")

        usuario = cls(nombre=nombre, correo=correo, sexo=sexo, edad=edad, carrera=carrera,
                      password_hash=generate_password_hash(password))  # = password_hash() de PHP
        db.session.add(usuario)  # INSERT INTO usuarios ...
        db.session.commit()
        return usuario

    @classmethod
    def verificar(cls, correo, password):
        """Devuelve el usuario si el correo y la contraseña son correctos; si no, None."""
        usuario = cls.query.filter_by(correo=correo.strip()).first()  # SELECT ... WHERE correo = ?
        if usuario and check_password_hash(usuario.password_hash, password):  # = password_verify()
            return usuario
        return None

    @classmethod
    def buscar(cls, id):
        """SELECT ... WHERE id = ?"""
        return db.session.get(cls, id)
