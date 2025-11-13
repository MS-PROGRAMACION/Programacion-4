# ===============================================
# 📚 Biblioteca Personal con KeyDB / Redis
# Usando redis-py y almacenamiento en memoria
# ===============================================

import redis
import json
import uuid
import os
from dotenv import load_dotenv

# -----------------------------------------------
# CARGA DE VARIABLES DE ENTORNO
# -----------------------------------------------
load_dotenv()

KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD", None)

# -----------------------------------------------
# CONEXIÓN A KEYDB
# -----------------------------------------------
try:
    r = redis.Redis(
        host=KEYDB_HOST,
        port=KEYDB_PORT,
        password=KEYDB_PASSWORD,
        decode_responses=True
    )
    r.ping()
    print("✅ Conectado exitosamente a KeyDB.\n")
except redis.ConnectionError as e:
    print("❌ Error al conectar a KeyDB:", e)
    exit(1)


# -----------------------------------------------
# FUNCIONES CRUD
# -----------------------------------------------
def agregar_libro():
    """Agrega un libro como un objeto JSON."""
    titulo = input("Título: ")
    autor = input("Autor: ")
    genero = input("Género: ")
    leido = input("¿Leído? (Sí/No): ").capitalize()

    libro_id = str(uuid.uuid4())
    libro = {
        "id": libro_id,
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "leido": leido
    }

    # Guardar el libro en formato JSON
    r.set(f"libro:{libro_id}", json.dumps(libro))
    print(f"✅ Libro agregado con ID {libro_id}\n")


def ver_libros():
    """Lista todos los libros almacenados."""
    claves = r.keys("libro:*")
    if not claves:
        print("📭 No hay libros en la biblioteca.\n")
        return

    print("\n📚 Lista de libros registrados:")
    print("-" * 70)
    for clave in claves:
        libro = json.loads(r.get(clave))
        print(f"ID: {libro['id']} | Título: {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Leído: {libro['leido']}")
    print("-" * 70 + "\n")


def buscar_libros():
    """Permite buscar libros por título, autor o género."""
    campo = input("Buscar por (titulo/autor/genero): ").lower()
    termino = input("Ingrese término de búsqueda: ").lower()

    if campo not in ["titulo", "autor", "genero"]:
        print("❌ Campo no válido.\n")
        return

    claves = r.keys("libro:*")
    encontrados = []

    for clave in claves:
        libro = json.loads(r.get(clave))
        if termino in libro[campo].lower():
            encontrados.append(libro)

    if encontrados:
        print("\n🔎 Resultados encontrados:")
        for libro in encontrados:
            print(f"- {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Leído: {libro['leido']}")
        print()
    else:
        print("⚠️ No se encontraron coincidencias.\n")


def actualizar_libro():
    """Actualiza los datos de un libro existente."""
    libro_id = input("Ingrese el ID del libro a actualizar: ")
    clave = f"libro:{libro_id}"

    if not r.exists(clave):
        print("⚠️ Libro no encontrado.\n")
        return

    libro = json.loads(r.get(clave))
    print(f"Libro actual: {libro}")

    campo = input("Campo a modificar (titulo, autor, genero, leido): ").lower()
    if campo not in libro:
        print("❌ Campo inválido.\n")
        return

    nuevo_valor = input(f"Nuevo valor para {campo}: ")
    libro[campo] = nuevo_valor
    r.set(clave, json.dumps(libro))
    print("✅ Libro actualizado correctamente.\n")


def eliminar_libro():
    """Elimina un libro por ID."""
    libro_id = input("Ingrese el ID del libro a eliminar: ")
    clave = f"libro:{libro_id}"

    if r.delete(clave):
        print("🗑️ Libro eliminado correctamente.\n")
    else:
        print("⚠️ No se encontró el libro con ese ID.\n")


# -----------------------------------------------
# MENÚ PRINCIPAL
# -----------------------------------------------
def menu():
    while True:
        print("""
============== 📖 MENÚ DE BIBLIOTECA (KeyDB) ==============
1. Agregar nuevo libro
2. Ver listado de libros
3. Buscar libros
4. Actualizar información de un libro
5. Eliminar libro existente
6. Salir
============================================================
""")
        opcion = input("Seleccione una opción (1-6): ")

        if opcion == "1":
            agregar_libro()
        elif opcion == "2":
            ver_libros()
        elif opcion == "3":
            buscar_libros()
        elif opcion == "4":
            actualizar_libro()
        elif opcion == "5":
            eliminar_libro()
        elif opcion == "6":
            print("👋 Saliendo del programa...")
            break
        else:
            print("❌ Opción inválida.\n")


# -----------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------
if __name__ == "__main__":
    menu()
