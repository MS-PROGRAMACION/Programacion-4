# ===============================================
# Aplicación de línea de comandos en Python para
# la gestión de una biblioteca personal con SQLite
# ===============================================

import sqlite3

# -----------------------------------------------
# Conexión y creación de la base de datos
# -----------------------------------------------
def conectar():
    """Conecta con la base de datos y crea la tabla si no existe."""
    conexion = sqlite3.connect("biblioteca.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS libros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            genero TEXT,
            leido TEXT CHECK(leido IN ('Sí', 'No')) NOT NULL DEFAULT 'No'
        );
    """)
    conexion.commit()
    return conexion


# -----------------------------------------------
# Funciones CRUD (Crear, Leer, Actualizar, Borrar)
# -----------------------------------------------
def agregar_libro(conexion):
    """Agrega un nuevo libro a la biblioteca."""
    titulo = input("Título del libro: ")
    autor = input("Autor: ")
    genero = input("Género: ")
    leido = input("¿Leído? (Sí/No): ").capitalize()

    cursor = conexion.cursor()
    cursor.execute("INSERT INTO libros (titulo, autor, genero, leido) VALUES (?, ?, ?, ?)",
                   (titulo, autor, genero, leido))
    conexion.commit()
    print("✅ Libro agregado correctamente.\n")


def ver_libros(conexion):
    """Muestra todos los libros registrados."""
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM libros")
    libros = cursor.fetchall()

    if not libros:
        print("📭 No hay libros registrados.\n")
    else:
        print("\n📚 Lista de libros:")
        print("-" * 60)
        for libro in libros:
            print(f"ID: {libro[0]} | Título: {libro[1]} | Autor: {libro[2]} | Género: {libro[3]} | Leído: {libro[4]}")
        print("-" * 60 + "\n")


def buscar_libro(conexion):
    """Permite buscar libros por título, autor o género."""
    campo = input("Buscar por (titulo/autor/genero): ").lower()
    valor = input("Ingrese término de búsqueda: ")

    cursor = conexion.cursor()
    query = f"SELECT * FROM libros WHERE {campo} LIKE ?"
    cursor.execute(query, ('%' + valor + '%',))
    resultados = cursor.fetchall()

    if resultados:
        print("\n🔎 Resultados de búsqueda:")
        for libro in resultados:
            print(f"ID: {libro[0]} | {libro[1]} | {libro[2]} | {libro[3]} | Leído: {libro[4]}")
        print()
    else:
        print("❌ No se encontraron libros con ese criterio.\n")


def actualizar_libro(conexion):
    """Actualiza la información de un libro existente."""
    id_libro = input("Ingrese el ID del libro a actualizar: ")
    campo = input("Campo a modificar (titulo, autor, genero, leido): ").lower()
    nuevo_valor = input(f"Nuevo valor para {campo}: ")

    cursor = conexion.cursor()
    query = f"UPDATE libros SET {campo} = ? WHERE id = ?"
    cursor.execute(query, (nuevo_valor, id_libro))
    conexion.commit()

    if cursor.rowcount:
        print("✅ Libro actualizado correctamente.\n")
    else:
        print("⚠️ No se encontró un libro con ese ID.\n")


def eliminar_libro(conexion):
    """Elimina un libro por ID."""
    id_libro = input("Ingrese el ID del libro a eliminar: ")

    cursor = conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id = ?", (id_libro,))
    conexion.commit()

    if cursor.rowcount:
        print("🗑️ Libro eliminado correctamente.\n")
    else:
        print("⚠️ No se encontró un libro con ese ID.\n")


# -----------------------------------------------
# Menú principal de la aplicación
# -----------------------------------------------
def menu():
    conexion = conectar()
    while True:
        print("""
============== 📖 MENÚ DE BIBLIOTECA ==============
1. Agregar nuevo libro
2. Ver listado de libros
3. Buscar libros
4. Actualizar información de un libro
5. Eliminar libro existente
6. Salir
===================================================
""")
        opcion = input("Seleccione una opción (1-6): ")

        if opcion == "1":
            agregar_libro(conexion)
        elif opcion == "2":
            ver_libros(conexion)
        elif opcion == "3":
            buscar_libro(conexion)
        elif opcion == "4":
            actualizar_libro(conexion)
        elif opcion == "5":
            eliminar_libro(conexion)
        elif opcion == "6":
            print("👋 Saliendo del programa... ¡Hasta luego!")
            conexion.close()
            break
        else:
            print("❌ Opción inválida. Intente de nuevo.\n")


# -----------------------------------------------
# 4️⃣ Ejecución principal
# -----------------------------------------------
if __name__ == "__main__":
    menu()
