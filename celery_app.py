# celery_app.py
# Configuración mínima de Celery para integrarse con una app Flask

from celery import Celery

def make_celery(app):
    """
    Crea y configura una instancia de Celery usando la configuración del app Flask.
    Devuelve el objeto Celery vinculado al contexto de la app.
    """
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL"),
        backend=app.config.get("CELERY_RESULT_BACKEND", app.config.get("CELERY_BROKER_URL"))
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Asegura que las tareas corran dentro del contexto de la app Flask."""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# app.py
# Aplicación Flask que usa KeyDB (Redis compatible) como almacenamiento y broker;
# envía correos asíncronos con Celery.

import os
import json
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message
import redis
from celery_app import make_celery

# Cargar variables de entorno desde .env
load_dotenv()

# -------------------------
# Configuración Flask
# -------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "cambiame_ya")

# Mail (Flask-Mail)
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER", "")
app.config["MAIL_PORT"] = int(os.getenv("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS", "True").lower() in ("1", "true", "yes")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_DEFAULT_SENDER", app.config["MAIL_USERNAME"])

mail = Mail(app)

# Celery (usa KeyDB / Redis compatible como broker)
app.config["CELERY_BROKER_URL"] = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
app.config["CELERY_RESULT_BACKEND"] = os.getenv("CELERY_RESULT_BACKEND", app.config["CELERY_BROKER_URL"])

celery = make_celery(app)

# -------------------------
# KeyDB / Redis (datos)
# -------------------------
KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD") or None

db = redis.Redis(host=KEYDB_HOST, port=KEYDB_PORT, password=KEYDB_PASSWORD, decode_responses=True)

# -------------------------
# Auxiliares (almacenamiento simple en KeyDB)
# -------------------------
def obtener_libros():
    keys = db.keys("libro:*")
    libros = []
    for k in keys:
        try:
            libros.append(json.loads(db.get(k)))
        except Exception:
            continue
    return sorted(libros, key=lambda x: x.get("titulo", "").lower())

def obtener_libro(id_libro):
    data = db.get(f"libro:{id_libro}")
    return json.loads(data) if data else None

# -------------------------
# Tarea asíncrona: envío de correo
# -------------------------
@celery.task(bind=True)
def enviar_correo_async(self, asunto, destinatario, cuerpo, html=None):
    """
    Tarea Celery que envía un correo. Se ejecuta dentro del contexto Flask gracias a make_celery.
    Parámetros:
      - asunto (str)
      - destinatario (str)
      - cuerpo (str): texto plano
      - html (str): opcional, contenido HTML
    """
    try:
        msg = Message(subject=asunto, recipients=[destinatario])
        msg.body = cuerpo
        if html:
            msg.html = html
        mail.send(msg)
        return {"status": "ok"}
    except Exception as e:
        # registrar error (simple print; en prod usar logging)
        print("Error enviando correo:", e)
        return {"status": "error", "detail": str(e)}

# -------------------------
# Rutas principales (ejemplo mínimo)
# -------------------------
@app.route("/")
def index():
    libros = obtener_libros()
    return render_template("index.html", libros=libros)  # si no tienes templates, puedes devolver JSON o texto

@app.route("/add", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        leido = request.form.get("leido", "No")

        if not titulo or not autor or not genero:
            flash("Todos los campos son obligatorios", "warning")
            return redirect(url_for("add_book"))

        libro_id = str(uuid.uuid4())
        libro = {"id": libro_id, "titulo": titulo, "autor": autor, "genero": genero, "leido": leido}
        db.set(f"libro:{libro_id}", json.dumps(libro))

        # Llamada asíncrona para enviar correo
        destino = os.getenv("MAIL_NOTIFICATION_TO", app.config["MAIL_USERNAME"])
        asunto = "Confirmación: libro agregado"
        cuerpo = f"Se ha agregado el libro '{titulo}' (autor: {autor}) a la biblioteca."
        # opcional: html = "<p>...</p>"
        enviar_correo_async.delay(asunto, destino, cuerpo)

        flash("Libro agregado. Se envió notificación por correo (tarea en background).", "success")
        return redirect(url_for("index"))

    # GET: muestra formulario (si no tienes template, puedes devolver un placeholder)
    return render_template("add_book.html")

@app.route("/delete/<id_libro>", methods=["GET", "POST"])
def delete_book(id_libro):
    libro = obtener_libro(id_libro)
    if not libro:
        flash("Libro no encontrado", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        db.delete(f"libro:{id_libro}")

        # Envío asíncrono de notificación
        destino = os.getenv("MAIL_NOTIFICATION_TO", app.config["MAIL_USERNAME"])
        asunto = "Confirmación: libro eliminado"
        cuerpo = f"Se ha eliminado el libro '{libro.get('titulo', '')}' de la biblioteca."
        enviar_correo_async.delay(asunto, destino, cuerpo)

        flash("Libro eliminado. Se envió notificación por correo (tarea en background).", "info")
        return redirect(url_for("index"))

    return render_template("confirm_delete.html", libro=libro)

# -------------------------
# Inicio de la app
# -------------------------
if __name__ == "__main__":
    # Nota: en producción usar Gunicorn + worker Celery separado
    app.run(debug=True)
