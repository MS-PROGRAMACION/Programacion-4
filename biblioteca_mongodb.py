# ===============================================
# Aplicación de Biblioteca Personal con MongoDB
# Usando PyMongo
# ===============================================

from pymongo import MongoClient, errors
from bson.objectid import ObjectId

# -----------------------------------------------
# CONFIGURACIÓN DE CONEXIÓN A MONGODB
# -----------------------------------------------
# ⚙️ Cambia la cadena de conexión según tu entorno
# Para MongoDB local:
#   uri = "mongodb://localhost:27017"
# Para MongoDB Atlas (ejemplo):
#   uri = "mongodb+srv://usuario:contraseña@cluster.mongodb.net/"
uri = "mongodb://localhost:27017"

try:
    cliente = MongoClient(uri)
    db = cliente["biblioteca"]
    coleccion = db["libros"]
    print("✅ Conexión a MongoDB establecida correctamente.\n")
except errors.ConnectionFailure as e:
    print("❌ Error de conexión a MongoDB:", e)
    exit(1)


# -----------------------------------------------
# FUNCIONES CRUD
# -----------------------------------------------
def agregar_libro():
    """Agrega un nuevo documento (libro) a MongoDB."""
    try:
        titulo = input("Título del libro: ")
        autor = input("Autor: ")
        genero = input("Género: ")
        leido = input("¿Leído? (Sí/No): ").capitalize()

        libro = {
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "leido": leido
        }

        resultado = coleccion.insert_one(libro)
        print(f"✅ Libro agregado con ID: {resultado.inserted_id}\n")

    except Exception as e:
        print("❌ Error al agregar libro:", e)


def ver_libros():
    """Muestra todos los documentos en la colección."""
    libros = list(coleccion.find())
    if not libros:
        print("📭 No hay libros registrados.\n")
    else:
        print("\n📚 Lista de libros en la biblioteca:")
        print("-" * 70)
        for libro in libros:
            print(f"ID: {libro['_id']} | Título: {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Leído: {libro['leido']}")
        print("-" * 70 + "\n")


def buscar_libros():
    """Busca libros por título, autor o género."""
    campo = input("Buscar por (titulo/autor/genero): ").lower()
    valor = input("Ingrese término de búsqueda: ")

    if campo not in ["titulo", "autor", "genero"]:
        print("❌ Campo de búsqueda no válido.\n")
        return

    resultados = list(coleccion.find({campo: {"$regex": valor, "$options": "i"}}))

    if resultados:
        print("\n🔎 Resultados de búsqueda:")
        for libro in resultados:
            print(f"ID: {libro['_id']} | {libro['titulo']} | {libro['autor']} | {libro['genero']} | Leído: {libro['leido']}")
        print()
    else:
        print("⚠️ No se encontraron libros con ese criterio.\n")


def actualizar_libro():
    """Actualiza campos de un libro por ID."""
    try:
        id_libro = input("Ingrese el ID del libro a actualizar: ")
        campo = input("Campo a modificar (titulo, autor, genero, leido): ").lower()
        nuevo_valor = input(f"Nuevo valor para {campo}: ")

        resultado = coleccion.update_one(
            {"_id": ObjectId(id_libro)},
            {"$set": {campo: nuevo_valor}}
        )

        if resultado.modified_count > 0:
            print("✅ Libro actualizado correctamente.\n")
        else:
            print("⚠️ No se modificó ningún documento (ID inválido o sin cambios).\n")

    except Exception as e:
        print("❌ Error al actualizar libro:", e)


def eliminar_libro():
    """Elimina un libro por ID."""
    try:
        id_libro = input("Ingrese el ID del libro a eliminar: ")
        resultado = coleccion.delete_one({"_id": ObjectId(id_libro)})

        if resultado.deleted_count > 0:
            print("🗑️ Libro eliminado correctamente.\n")
        else:
            print("⚠️ No se encontró un libro con ese ID.\n")

    except Exception as e:
        print("❌ Error al eliminar libro:", e)


# -----------------------------------------------
# MENÚ PRINCIPAL
# -----------------------------------------------
def menu():
    while True:
        print("""
============== 📖 MENÚ DE BIBLIOTECA (MongoDB) ==============
1. Agregar nuevo libro
2. Ver listado de libros
3. Buscar libros
4. Actualizar información de un libro
5. Eliminar libro existente
6. Salir
==============================================================
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
            cliente.close()
            break
        else:
            print("❌ Opción inválida.\n")


# -----------------------------------------------
# 4️⃣ EJECUCIÓN PRINCIPAL
# -----------------------------------------------
if __name__ == "__main__":
    menu()
