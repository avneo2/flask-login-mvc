# LOGIN con Flask y el patrón MVC

Es el **mismo ejercicio LOGIN** que hicimos en PHP (registro, inicio de sesión, página protegida y cierre de sesión), ahora en **Python con Flask** y organizado con el patrón **Modelo–Vista–Controlador (MVC)**.

No hace falta XAMPP: los datos se guardan en un archivo SQLite que se crea solo. Al final se comparte por internet con **Cloudflare Tunnel**, igual que en LOGIN.

Los diagramas están en [DIAGRAMAS.md](DIAGRAMAS.md).

---

## 1. ¿Qué hace la aplicación?

1. El usuario **se registra** con nombre, correo, sexo, edad, carrera y contraseña.
2. La contraseña **no se guarda tal cual**: se guarda su **hash**.
3. El usuario **inicia sesión** con correo y contraseña.
4. Si los datos son correctos, entra a una **página protegida** con sus datos.
5. Puede **cerrar sesión**.

## 2. ¿Qué es MVC?

MVC es una forma de **ordenar el código en tres partes**, y cada parte tiene **un solo trabajo**.

**Analogía: un restaurante**

| Parte | En el restaurante | En la app | Archivo |
|---|---|---|---|
| **Modelo** | La **cocina y el almacén**: guarda los ingredientes y sabe las recetas (las reglas). | La clase `Usuario`: guarda usuarios y sabe las reglas (edad 15–99, contraseña ≥ 8, correo único). | `modelo.py` |
| **Vista** | El **plato servido**: lo que ve el cliente. No cocina nada. | Las plantillas HTML. Solo muestran lo que les entregan. | `templates/*.html` |
| **Controlador** | El **mesero**: toma el pedido, lo lleva a la cocina y trae el plato. No cocina ni decide la receta. | Las rutas: reciben la petición, llaman al Modelo y eligen la Vista o redirigen. | `controlador.py` |

`app.py` no es ninguna de las tres partes: es quien **abre el restaurante**. Crea la app y une el Modelo con el Controlador.

**¿Para qué sirve separar?**

- **Para encontrar las cosas.** ¿Cambiar la edad mínima? Está en el Modelo. ¿Cambiar un texto? Está en la Vista.
- **Para reutilizar.** El mismo Modelo sirve para una página HTML o para una API que responde JSON.
- **Para trabajar en equipo.** Una persona hace las plantillas y otra el Modelo, sin estorbarse.

> **Comparación con PHP:** en `LOGIN/registro.php` todo estaba junto en un archivo: la validación, el `INSERT` y el HTML. Aquí esas tres cosas viven en tres lugares distintos.

**Regla práctica para saber dónde va algo**

| Si el código… | va en |
|---|---|
| usa `db`, valida datos o calcula un hash | **Modelo** |
| usa `request`, `session`, `redirect` o `render_template` | **Controlador** |
| es HTML, `{{ }}` o `{% %}` | **Vista** |

> **Nota para curiosos:** Flask no obliga a usar MVC; lo usamos por convención. Django sí trae una estructura parecida y la llama **MTV** (Modelo–Template–Vista). Es la misma idea con otros nombres, y la veremos en el siguiente ejercicio.

## 3. Estructura de archivos

```
LOGIN_MVC/
├── app.py              ← ARRANQUE: crea la app y une las piezas
├── modelo.py           ← M: clase Usuario (tabla usuarios) y sus reglas
├── controlador.py      ← C: las rutas /login, /registro, /bienvenida, /logout
├── templates/          ← V: las vistas (HTML con Jinja)
│   ├── base.html       ←    molde común: <head>, estilos y mensaje de error
│   ├── login.html
│   ├── registro.html
│   └── bienvenida.html
├── static/             ← archivos que el navegador descarga tal cual
│   ├── estilos.css     ←    el mismo de LOGIN
│   └── app.js          ←    el mismo de LOGIN
├── requirements.txt    ← dependencias (Flask y Flask-SQLAlchemy)
├── instance/login.db   ← la base de datos SQLite (se crea sola al arrancar)
├── EXPLICACION.md      ← este documento
├── DIAGRAMAS.md        ← diagramas de casos de uso, MVC y secuencia
└── skill/              ← el tutor de IA del ejercicio (sección 11)
```

## 4. De PHP a Flask: equivalencias

| PHP (LOGIN) | Flask (LOGIN_MVC) |
|---|---|
| Un archivo por página: `login.php` | Una función por ruta: `def login()` con `@controlador.route("/login")` |
| `$_POST['correo']` | `request.form.get("correo")` |
| `$_GET['registrado']` | `request.args` |
| `session_start()` y `$_SESSION['nombre']` | `session["nombre"]` (la clave va en `SECRET_KEY`) |
| `header('Location: login.php')` | `redirect(url_for("controlador.login"))` |
| `password_hash()` / `password_verify()` | `generate_password_hash()` / `check_password_hash()` |
| `$pdo->prepare('SELECT … WHERE correo = ?')` | `Usuario.query.filter_by(correo=correo).first()` |
| `<?= e($nombre) ?>` | `{{ nombre }}` (escapa solo, no hace falta `e()`) |
| `database.sql` con `CREATE TABLE` | La clase `Usuario` + `db.create_all()` |
| `C:\xampp\htdocs\login\` | Cualquier carpeta. Se ejecuta con `python app.py` |

**Lo nuevo, en una línea cada uno:**

- **Flask-SQLAlchemy (ORM):** cada tabla es una **clase** y cada fila es un **objeto**, así que escribimos Python en vez de SQL. Aquí está la **programación orientada a objetos** del ejercicio.
- **Blueprint:** un "paquete de rutas". Permite tener el Controlador en su propio archivo.
- **Jinja:** el lenguaje de las plantillas. `{{ }}` imprime un valor y `{% %}` es lógica (`if`, `for`, `extends`).
- **`{% extends "base.html" %}`:** cada página "hereda" el molde y solo llena su `{% block contenido %}`. Así ya no se repite el `<head>`.

## 5. Recorrido de una petición: "Entrar"

1. El navegador envía `POST /login` con correo y contraseña.
2. **Controlador** `login()`: toma los datos de `request.form` y llama a `Usuario.verificar(correo, password)`.
3. **Modelo** `verificar()`: busca el correo en la tabla y compara el hash. Devuelve el usuario o `None`.
4. **Controlador**: si recibe un usuario, guarda `usuario_id` en la sesión y **redirige** a `/bienvenida`. Si recibe `None`, vuelve a mostrar la vista `login.html` con el error.
5. **Controlador** `bienvenida()`: revisa la sesión, pide el usuario con `Usuario.buscar(id)` y se lo entrega a la vista.
6. **Vista** `bienvenida.html`: muestra `{{ usuario.nombre }}` y los demás datos.

El diagrama de secuencia de [DIAGRAMAS.md](DIAGRAMAS.md) dibuja este mismo recorrido.

## 6. Ejecutarlo en tu computadora

Requisito: **Python 3.10 o más nuevo** (`python --version`).

En la terminal de VS Code (PowerShell), **dentro de la carpeta `LOGIN_MVC`**:

```powershell
python -m venv venv                 # 1. crea un entorno virtual (solo la primera vez)
venv\Scripts\activate               # 2. lo activa: verás (venv) al inicio de la línea
pip install -r requirements.txt     # 3. instala Flask (solo la primera vez)
python app.py                       # 4. enciende la app
```

Abre **http://localhost:5000**. Para apagarla, pulsa `Ctrl + C` en la terminal.

> Si PowerShell bloquea `activate`, ejecuta una sola vez:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

`python app.py` arranca en **modo debug**: se reinicia sola al guardar cambios y muestra los errores con detalle. Es ideal para programar, **pero no para compartir** (sección 7).

## 7. Compartirla por internet con Cloudflare Tunnel

Es lo mismo que en LOGIN (sección 13 de `LOGIN/EXPLICACION.md`, donde está explicado qué es un túnel). Solo cambian el comando para encender la app y el puerto, que ahora es el **5000**.

```
Celular del alumno ──HTTPS──► Cloudflare ══ túnel ══► cloudflared (tu PC) ──► Flask en localhost:5000 ──► login.db
```

### 7.1 Instalar `cloudflared` (solo una vez por computadora)

1. Abre **PowerShell** y revisa si ya está instalado:
   ```powershell
   cloudflared --version
   ```
   Si aparece algo como `cloudflared version 2026.10.0`, **ya está listo**: salta a 7.2.
2. Si dice *"no se reconoce como un comando"*, instálalo con **winget**:
   ```powershell
   winget install --id Cloudflare.cloudflared
   ```
   Acepta si te pide confirmación.
3. **Cierra PowerShell, ábrelo de nuevo** y repite el paso 1.

*Sin winget:* descarga `cloudflared-windows-amd64.msi` desde <https://github.com/cloudflare/cloudflared/releases> e instálalo con doble clic. Después, cierra y vuelve a abrir PowerShell.

No hace falta crear una cuenta en Cloudflare: usamos **Quick Tunnel**, que es gratis y no pide registro.

### 7.2 Paso a paso (dos terminales abiertas al mismo tiempo)

**Terminal 1: encender la app *sin* modo debug**

Dentro de `LOGIN_MVC`, con el `(venv)` activado:

```powershell
flask --app app run --port 5000
```

| Parte | Significado |
|---|---|
| `flask --app app` | "Usa la app que está en `app.py`". |
| `run --port 5000` | Enciéndela en el puerto 5000, **sin modo debug** y solo para esta PC (`localhost`). |

✅ **Comprueba:** abre `http://localhost:5000`. Debe aparecer **Iniciar sesión**.

**Terminal 2: abrir el túnel**

Abre **otra** terminal (en VS Code, con el botón **+**) y escribe:

```powershell
cloudflared tunnel --url http://localhost:5000
```

Aparecerán muchas líneas `INF` y `WRN`. **Es normal.** Busca solo este recuadro:

```
INF |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
INF |  https://palabras-al-azar.trycloudflare.com                                               |
```

⏱️ Espera **entre 10 y 30 segundos** antes de abrirla.

**Probar y compartir**

1. Ábrela en tu **celular con datos móviles** (con el Wi-Fi apagado). Si carga, ya está en internet.
2. Comparte el enlace en Classroom o WhatsApp.
3. Para terminar, pulsa `Ctrl + C` en **las dos** terminales.

### 7.3 Para tener en cuenta

| Situación | Qué pasa |
|---|---|
| Cierras alguna de las dos terminales | El enlace deja de funcionar. |
| Vuelves a abrir el túnel | La URL **cambia**: hay que compartirla de nuevo. |
| Compartes con `python app.py` (modo debug) | ⚠️ **No lo hagas.** El modo debug muestra tu código cuando hay un error. Para compartir, usa siempre `flask --app app run`. |
| Cambias `SECRET_KEY` | Todas las sesiones abiertas se cierran. |
| Quieres empezar con la base vacía | Apaga la app y borra `instance/login.db`. |

## 8. (Opcional) Usar MySQL de XAMPP en lugar de SQLite

Así la app de Flask usa la **misma base `login_app`** de las prácticas PHP.

```powershell
pip install PyMySQL
$env:DATABASE_URL = "mysql+pymysql://root:@localhost/login_app"
python app.py
```

No hay que cambiar ni una línea del Modelo: **SQLAlchemy traduce** para SQLite o para MySQL.

> ⚠️ **Detalle interesante:** un usuario registrado en el LOGIN de PHP **no puede** entrar desde Flask, ni al revés. PHP guarda el hash con *bcrypt* (`$2y$…`) y Flask con *scrypt* (`scrypt:…`). Mira la columna `password_hash` en phpMyAdmin para comprobarlo.

## 9. Preguntas para la clase

1. ¿En qué archivo cambiarías la edad mínima de 15 a 18? ¿Por qué no en el Controlador?
2. `bienvenida.html` muestra `{{ usuario.nombre }}`. ¿Quién le entregó ese objeto? ¿La vista consulta la base de datos?
3. Si mañana una app de celular necesita iniciar sesión, ¿qué parte reutilizas tal cual y qué parte cambias?
4. ¿Qué pasa si alguien se registra con el nombre `<script>alert(1)</script>`? ¿Quién lo protege?
5. ¿Por qué el error al iniciar sesión dice "correo **o** contraseña incorrectos" y no aclara cuál de los dos falló?
6. En PHP había 6 archivos `.php`. Aquí, ¿cuántos archivos de Python hay y por qué?
7. ¿Por qué se usa `flask --app app run` y no `python app.py` para compartir por Cloudflare?

## 10. Retos

| Nivel | Reto | Qué parte tocas |
|---|---|---|
| ⭐ | Muestra en `bienvenida.html` la fecha de registro (`usuario.creado_en`). | Vista |
| ⭐ | Exige que la carrera tenga al menos 3 letras. | Modelo |
| ⭐⭐ | Cambia `?registrado=1` por un mensaje con `flash()` de Flask. | Controlador y Vista |
| ⭐⭐ | Agrega una página `/usuarios` que liste los nombres y carreras de todos (sin correos). Pista: un método `Usuario.todos()`. | Las tres |
| ⭐⭐⭐ | **Une UBICACION a este login.** Copia la clase `Ubicacion` de `../UBICACION_MVC/modelo.py` a tu Modelo, sus rutas a tu Controlador, su plantilla y `ubicacion.js`. Protege la página con la sesión y guarda el `usuario_id` real. | Las tres: ¡aquí se nota la ventaja de MVC! |

## 11. Tutor de IA del ejercicio (skill)

En `skill/tutor-flask-mvc/SKILL.md` hay un **tutor** que conoce este ejercicio. Te ayuda a entender, **te da pistas** para los retos (no la respuesta completa) y te ayuda con los errores.

**Opción A: como skill en Claude.** Si en tu cuenta aparece **Configuración → Capacidades → Skills**, sube el archivo `skill/tutor-flask-mvc.zip`. Después, en cualquier chat, escribe por ejemplo: *"Tengo una duda del ejercicio LOGIN MVC de Flask"*.

**Opción B: funciona en cualquier plan gratuito.** Abre `SKILL.md`, copia **todo** el texto y pégalo como primer mensaje de un chat nuevo (en Claude, ChatGPT o Gemini). Después escribe tu duda y pega el código o el error que tengas.

## 12. Problemas comunes

| Mensaje o síntoma | Causa y solución |
|---|---|
| `ModuleNotFoundError: No module named 'flask'` o `'flask_sqlalchemy'` | Python no encuentra las librerías. **Causa 1:** no activaste el entorno; ejecuta `venv\Scripts\activate` y verifica que aparezca `(venv)`. **Causa 2:** usaste el botón ▶ de VS Code, que corre otro Python. Selecciona el del entorno con `Ctrl + Shift + P` → *Python: Select Interpreter* → `.\venv\Scripts\python.exe`, o mejor ejecuta `python app.py` en la terminal con `(venv)` activo. |
| `TemplateNotFound: login.html` | La carpeta debe llamarse exactamente `templates` y estar junto a `app.py`. |
| La página se ve sin estilos | `estilos.css` debe estar en `static/`. Recarga con `Ctrl + F5`. |
| `Address already in use` o puerto 5000 ocupado | Ya hay otra app encendida. Apágala o usa `--port 5001`, también en el comando del túnel. |
| `cloudflared` no se reconoce | Cierra y abre PowerShell después de instalarlo (7.1). |
| La URL de Cloudflare marca error 1033 o 502 | Falta la terminal 1 (Flask apagado) o los puertos no coinciden. |
| `BuildError: Could not build url for endpoint 'login'` | En `url_for` falta el nombre del blueprint: `url_for('controlador.login')`. |
