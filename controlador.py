"""
C — CONTROLADOR: recibe la petición, le pide al Modelo lo necesario
y elige qué Vista (plantilla) responder o a dónde redirigir.

Equivalencias con PHP:
    index.php       →  inicio()
    login.php       →  login()
    registro.php    →  registro()
    bienvenida.php  →  bienvenida()
    logout.php      →  logout()
"""

from flask import Blueprint, redirect, render_template, request, session, url_for

from modelo import SEXOS, Usuario

controlador = Blueprint("controlador", __name__)


@controlador.get("/")
def inicio():
    return redirect(url_for("controlador.login"))


@controlador.route("/login", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        usuario = Usuario.verificar(request.form.get("correo", ""), request.form.get("password", ""))
        if usuario:
            session.clear()  # sesión nueva al entrar (en PHP: session_regenerate_id)
            session["usuario_id"] = usuario.id
            session["nombre"] = usuario.nombre
            return redirect(url_for("controlador.bienvenida"))
        error = "Correo o contraseña incorrectos."

    return render_template("login.html", error=error, datos=request.form,
                           registrado="registrado" in request.args)


@controlador.route("/registro", methods=["GET", "POST"])
def registro():
    error = ""
    if request.method == "POST":
        f = request.form  # = $_POST
        try:
            # El Modelo valida; el Controlador no conoce las reglas, solo pasa los datos.
            Usuario.registrar(
                nombre=f.get("nombre", ""), correo=f.get("correo", ""), sexo=f.get("sexo", ""),
                edad=f.get("edad", ""), carrera=f.get("carrera", ""),
                password=f.get("password", ""), confirmar=f.get("confirmar", ""),
            )
            return redirect(url_for("controlador.login", registrado=1))
        except ValueError as e:
            error = str(e)

    return render_template("registro.html", error=error, datos=request.form, sexos=SEXOS)


@controlador.get("/bienvenida")
def bienvenida():
    if "usuario_id" not in session:  # página protegida: sin sesión, primero a iniciar sesión
        return redirect(url_for("controlador.login"))
    return render_template("bienvenida.html", usuario=Usuario.buscar(session["usuario_id"]))


@controlador.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("controlador.login"))
