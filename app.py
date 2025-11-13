# ===============================================
# 📚 Biblioteca Personal Web con Flask y KeyDB
# Autor: [Tu Nombre]
# ===============================================

from flask import Flask, render_template, request, redirect, url_for, flash
import redis, json, uuid, os
from dotenv import load_dotenv

# -----------------------------------------------
# CONFIGURACIÓN DE ENTORNO Y CONEXIÓN A KEYDB
# -----------------------------------------------
load_dotenv()

app = Flask(__name__)
app.secret_key = "biblioteca_keydb"

KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD", None)

try:
    db = redis.Redis(
        host=KEYDB_HOST,
        port=KEYDB_PORT,
        password=KEYDB_PASSWORD,
        decode_responses=True
    )
    db.ping()
    print("✅ Conectado correctamente a KeyDB.")
except redis.ConnectionError:
    print("❌ Error al conectar con KeyDB.")
    exit(1)

# -----------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------
def obtener_libros():
    """Devuelve todos los libros guardados."""
    claves = db.keys("libro:*")
    libros = [json.loads(db.get(k)) for k in claves]
    return libros


def obtener_libro(id_libro):
    """Obtiene un libro por su ID."""
    data = db.get(f"libro:{id_libro}")
    return json.loads(data) if data else None


# -----------------------------------------------
# RUTAS PRINCIPALES DE FLASK
# -----------------------------------------------

@app.route("/")
def index():
    """Página principal con listado de libros."""
    query = request.args.get("q", "").lower()
    libros = obtener_libros()

    if query:
        libros = [l for l in libros if query in l["titulo"].lower() or
                                      query in l["autor"].lower() or
                                      query in l["genero"].lower()]

    return render_template("index.html", libros=libros, query=query)


@app.route("/add", methods=["GET", "POST"])
def add_book():
    """Agregar un nuevo libro."""
    if request.method == "POST":
        titulo = request.form["titulo"].strip()
        autor = request.form["autor"].strip()
        genero = request.form["genero"].strip()
        leido = request.form.get("leido", "No")

        if not titulo or not autor or not genero:
            flash("⚠️ Todos los campos son obligatorios.", "warning")
            return redirect(url_for("add_book"))

        libro_id = str(uuid.uuid4())
        libro = {
            "id": libro_id,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "leido": leido
        }

        db.set(f"libro:{libro_id}", json.dumps(libro))
        flash("✅ Libro agregado exitosamente.", "success")
        return redirect(url_for("index"))

    return render_template("add_book.html")


@app.route("/edit/<id_libro>", methods=["GET", "POST"])
def edit_book(id_libro):
    """Editar la información de un libro."""
    libro = obtener_libro(id_libro)
    if not libro:
        flash("⚠️ Libro no encontrado.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        libro["titulo"] = request.form["titulo"].strip()
        libro["autor"] = request.form["autor"].strip()
        libro["genero"] = request.form["genero"].strip()
        libro["leido"] = request.form.get("leido", "No")

        db.set(f"libro:{id_libro}", json.dumps(libro))
        flash("✅ Libro actualizado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("edit_book.html", libro=libro)


@app.route("/delete/<id_libro>")
def delete_book(id_libro):
    """Eliminar un libro."""
    db.delete(f"libro:{id_libro}")
    flash("🗑️ Libro eliminado.", "info")
    return redirect(url_for("index"))


# -----------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
