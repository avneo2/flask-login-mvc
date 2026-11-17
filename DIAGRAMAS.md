# Diagramas — LOGIN con Flask y MVC

Se ven dibujados en VS Code (vista previa del Markdown, `Ctrl + Shift + V`, con la extensión *Markdown Preview Mermaid Support*), en GitHub o en <https://mermaid.live>.

| # | Diagrama | Responde a… |
|---|---|---|
| 0 | Instalación y configuración | ¿Qué instalo y configuro, y en qué orden? |
| 1 | Casos de uso | ¿Qué puede hacer cada usuario? |
| 2 | Piezas del MVC | ¿Cómo está construida la app? |
| 3 | Secuencia de inicio de sesión | ¿Qué pasa, paso a paso, al dar clic en "Entrar"? |
| 4 | Navegación | ¿A qué página me lleva cada acción? |
| 5 | Despliegue con Cloudflare | ¿Cómo llega un celular a mi PC? |

---

## 0. Instalación y configuración: de cero a compartir

Los rombos son preguntas que tú respondes. Las cajas amarillas son instalaciones (una sola vez por computadora) y las verdes, comprobaciones de que todo va bien.

```mermaid
flowchart TD
    inicio(["Inicio"])

    subgraph unaVez ["① Una sola vez por computadora"]
        py{"¿python --version<br/>muestra 3.10 o más?"}
        instPy["Instalar Python desde python.org<br/>☑ marcar 'Add python.exe to PATH'"]
        vsc["Instalar VS Code<br/>(opcional: extensión Python)"]
        cfq{"¿cloudflared --version<br/>responde?"}
        instCf["winget install --id Cloudflare.cloudflared<br/>o descargar el .msi de GitHub"]
        reabrir["Cerrar y volver a abrir PowerShell"]
    end

    subgraph proyecto ["② Una sola vez por proyecto (dentro de LOGIN_MVC)"]
        venv["python -m venv venv"]
        act["venv\Scripts\activate"]
        bloq{"¿PowerShell bloquea<br/>el script?"}
        pol["Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"]
        pip["pip install -r requirements.txt<br/>(Flask + Flask-SQLAlchemy)"]
    end

    subgraph diario ["③ Cada vez que programas"]
        act2["venv\Scripts\activate<br/>→ aparece (venv)"]
        mysql{"¿Usar MySQL de XAMPP<br/>en vez de SQLite?"}
        cfgMy["pip install PyMySQL<br/>$env:DATABASE_URL = 'mysql+pymysql://root:@localhost/login_app'"]
        run["python app.py<br/>(modo debug)"]
        ok1["✅ http://localhost:5000<br/>muestra 'Iniciar sesión'"]
    end

    subgraph compartir ["④ Para compartir por internet"]
        t1["Terminal 1:<br/>flask --app app run --port 5000<br/>(SIN debug)"]
        t2["Terminal 2:<br/>cloudflared tunnel --url http://localhost:5000"]
        url["Copiar https://….trycloudflare.com<br/>esperar 10–30 s"]
        ok2["✅ Probar en el celular con datos móviles<br/>y compartir el enlace"]
        fin["Ctrl + C en las dos terminales"]
    end

    inicio --> py
    py -- "No" --> instPy --> py
    py -- "Sí" --> vsc --> cfq
    cfq -- "No" --> instCf --> reabrir --> cfq
    cfq -- "Sí" --> venv
    venv --> act --> bloq
    bloq -- "Sí" --> pol --> act
    bloq -- "No" --> pip --> act2
    act2 --> mysql
    mysql -- "Sí (opcional)" --> cfgMy --> run
    mysql -- "No (recomendado)" --> run
    run --> ok1
    ok1 -- "Ctrl + C y luego" --> t1 --> t2 --> url --> ok2 --> fin

    classDef unica fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef check fill:#dcfce7,stroke:#16a34a,color:#14532d
    class instPy,vsc,instCf,reabrir unica
    class ok1,ok2 check
```

### Configuraciones de la app (variables de entorno)

Todas son **opcionales**: si no se definen, `app.py` usa el valor por defecto.

| Variable | Por defecto | Para qué sirve | Cómo se define en PowerShell |
|---|---|---|---|
| `SECRET_KEY` | `clave-solo-para-clase` | Firma la cookie de sesión. Si alguien la conoce, puede falsificar sesiones. | `$env:SECRET_KEY = "algo-largo-y-secreto"` |
| `DATABASE_URL` | `sqlite:///login.db` (archivo `instance/login.db`) | Dónde se guardan los usuarios. | `$env:DATABASE_URL = "mysql+pymysql://root:@localhost/login_app"` |
| `PORT` | `5000` | Puerto de `python app.py`. Con `flask run` se usa `--port`. | `$env:PORT = "5001"` |

> Las variables `$env:` solo duran **mientras esa terminal esté abierta**. Hay que definirlas **antes** de encender la app.

### Lo que se instala y dónde queda

| Qué | Dónde | Alcance |
|---|---|---|
| Python | `C:\Users\<tú>\AppData\Local\Programs\Python\` | Toda la PC |
| `cloudflared` | `C:\Program Files (x86)\cloudflared\` | Toda la PC |
| Flask y Flask-SQLAlchemy | `LOGIN_MVC\venv\` | **Solo este proyecto.** Si borras `venv`, lo reinstalas con `pip`. |
| La base de datos | `LOGIN_MVC\instance\login.db` | Solo este proyecto. Si la borras, empiezas sin usuarios. |

---

## 1. Diagrama de casos de uso

Qué puede hacer cada actor. Mermaid no tiene diagrama de casos de uso de UML, así que se dibuja con un diagrama de flujo: los óvalos son los casos de uso.

```mermaid
flowchart LR
    visitante(["👤 Visitante<br/>(sin sesión)"])
    usuario(["👤 Usuario<br/>(con sesión)"])

    subgraph sistema ["Sistema LOGIN_MVC"]
        cu1(["Registrarse"])
        cu2(["Iniciar sesión"])
        cu3(["Ver mis datos"])
        cu4(["Cerrar sesión"])
        cu5(["Validar datos del registro"])
        cu6(["Verificar contraseña"])
    end

    visitante --> cu1
    visitante --> cu2
    usuario --> cu3
    usuario --> cu4

    cu1 -. "«include»" .-> cu5
    cu2 -. "«include»" .-> cu6
    cu2 -- "si es correcto, el visitante<br/>se convierte en usuario" --> usuario
```

| Caso de uso | Ruta | Resultado |
|---|---|---|
| Registrarse | `GET/POST /registro` | Crea la fila en `usuarios` y redirige a `/login?registrado=1`. |
| Iniciar sesión | `GET/POST /login` | Guarda `usuario_id` en la sesión y redirige a `/bienvenida`. |
| Ver mis datos | `GET /bienvenida` | Muestra los datos. **Sin sesión** redirige a `/login`. |
| Cerrar sesión | `GET /logout` | Borra la sesión y redirige a `/login`. |

---

## 2. Las piezas del MVC

Quién conoce a quién. Las flechas indican "llama a" o "usa".

```mermaid
flowchart LR
    nav["🌐 Navegador"]

    subgraph app ["Aplicación Flask"]
        direction LR
        arranque["app.py<br/><i>arranque</i>"]
        C["<b>C · controlador.py</b><br/>login() · registro()<br/>bienvenida() · logout()"]
        M["<b>M · modelo.py</b><br/>class Usuario<br/>registrar() · verificar() · buscar()"]
        V["<b>V · templates/</b><br/>base · login · registro<br/>bienvenida"]
    end

    bd[("instance/login.db<br/>tabla usuarios")]

    nav -- "1. petición HTTP" --> C
    C -- "2. pide o guarda datos" --> M
    M -- "SQL (lo genera SQLAlchemy)" --> bd
    C -- "3. entrega datos a la vista" --> V
    V -- "4. HTML" --> nav
    arranque -. "registra" .-> C
    arranque -. "conecta" .-> M
```

**Lo que nunca pasa:** la Vista no habla con el Modelo ni con la base de datos, y el Modelo no sabe nada de HTML ni de `request`.

---

## 3. Secuencia: iniciar sesión

```mermaid
sequenceDiagram
    actor U as Usuario
    participant N as Navegador
    participant C as Controlador<br/>login()
    participant M as Modelo<br/>Usuario
    participant BD as login.db
    participant V as Vista<br/>*.html

    U->>N: Escribe correo y contraseña, clic en "Entrar"
    N->>C: POST /login (correo, password)
    C->>M: Usuario.verificar(correo, password)
    M->>BD: SELECT * FROM usuarios WHERE correo = ?
    BD-->>M: fila o nada
    M->>M: check_password_hash(hash, password)

    alt datos correctos
        M-->>C: objeto Usuario
        C->>C: session["usuario_id"] = usuario.id
        C-->>N: 302 Redirigir a /bienvenida
        N->>C: GET /bienvenida
        C->>M: Usuario.buscar(session["usuario_id"])
        M-->>C: objeto Usuario
        C->>V: render_template("bienvenida.html", usuario)
        V-->>N: HTML "¡Hola, Ana!"
    else datos incorrectos
        M-->>C: None
        C->>V: render_template("login.html", error)
        V-->>N: HTML con "Correo o contraseña incorrectos."
    end
```

---

## 4. Navegación entre páginas

```mermaid
stateDiagram-v2
    [*] --> Login: GET /
    Login --> Registro: enlace Regístrate
    Registro --> Registro: datos inválidos (muestra error)
    Registro --> Login: registro correcto (?registrado=1)
    Login --> Login: datos incorrectos (muestra error)
    Login --> Bienvenida: datos correctos
    Bienvenida --> Login: botón Cerrar sesión
    Bienvenida --> Login: sin sesión (redirige)
```

---

## 5. Despliegue en servidor local con Cloudflare Tunnel

```mermaid
flowchart LR
    cel["📱 Celular o PC<br/>del alumno"]
    cf["☁️ Cloudflare<br/>xxxx.trycloudflare.com"]

    subgraph pc ["💻 PC del profesor o del alumno"]
        cfd["cloudflared<br/><i>terminal 2</i>"]
        flask["Flask en localhost:5000<br/><i>terminal 1</i>"]
        db[("login.db")]
    end

    cel -- "HTTPS" --> cf
    cfd == "túnel: conexión SALIENTE<br/>que abrió la PC" ==> cf
    cf -. "la petición viaja por el túnel" .-> cfd
    cfd --> flask
    flask --> db
```
