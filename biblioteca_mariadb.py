# ===============================================
# Aplicación de Biblioteca Personal con MariaDB
# Usando SQLAlchemy (ORM)
# ===============================================

from sqlalchemy import create_engine, Column, Integer, String, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys

# -----------------------------------------------
# CONFIGURACIÓN DE CONEXIÓN A MARIADB
# -----------------------------------------------
# ⚠️ Antes de ejecutar, asegúrate de crear la base de datos en MariaDB:
#     CREATE DATABASE biblioteca CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# ⚙️ Cambia los valores según tu entorno:
USUARIO = "root"
PASSWORD = "tu_contraseña"
HOST = "localhost"
BASE_DATOS = "biblioteca"

# Cadena de conexión para MariaDB
DB_URL = f"mariadb+mariadbconnector://{USUARIO}:{PASSWORD}@{HOST}/{BASE_DATOS}"

try:
    engine = create_engine(DB_URL)
except Exception as e:
    print("❌ Error al conectar con MariaDB:", e)
    sys.exit(1)

Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

# -----------------------------------------------
# DEFINICIÓN DEL MODELO ORM
# -----------------------------------------------
class Libro(Base):
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    autor = Column(String(100), nullable=False)
    genero = Column(String(50))
    leido = Column(String(2), nullable=False, default="No")

    __table_args__ = (
        CheckConstraint("leido IN ('Sí', 'No')", name="check_leido"),
    )

    def __repr__(self):
        return f"<Libro(id={self.id}, titulo='{self.titulo}', autor='{self.autor}', genero='{self.genero}', leido='{self.leido}')>"


# -----------------------------------------------
# CREAR LAS TABLAS EN LA BASE DE DATOS
# -----------------------------------------------
Base.metadata.create_all(engine)

# -----------------------------------------------
# FUNCIONES CRUD
# -----------------------------------------------
def agregar_libro():
    try:
        titulo = input("Título del libro: ")
        autor = input("Autor: ")
        genero = input("Género: ")
        leido = input("¿Leído? (Sí/No): ").capitalize()

        nuevo = Libro(titulo=titulo, autor=autor, genero=genero, leido=leido)
        session.add(nuevo)
        session.commit()
        print("✅ Libro agregado correctamente.\n")
    except Exception as e:
        session.rollback()
        print("❌ Error al agregar libro:", e)


def ver_libros():
    libros = session.query(Libro).all()
    if not libros:
        print("📭 No hay libros registrados.\n")
    else:
        print("\n📚 Lista de libros:")
        print("-" * 70)
        for libro in libros:
            print(f"ID: {libro.id} | Título: {libro.titulo} | Autor: {libro.autor} | Género: {libro.genero} | Leído: {libro.leido}")
        print("-" * 70 + "\n")


def buscar_libro():
    campo = input("Buscar por (titulo/autor/genero): ").lower()
    valor = input("Ingrese término de búsqueda: ")

    if campo not in ["titulo", "autor", "genero"]:
        print("❌ Campo no válido.")
        return

    resultados = session.query(Libro).filter(getattr(Libro, campo).like(f"%{valor}%")).all()

    if resultados:
        print("\n🔎 Resultados de búsqueda:")
        for libro in resultados:
            print(f"ID: {libro.id} | {libro.titulo} | {libro.autor} | {libro.genero} | Leído: {libro.leido}")
        print()
    else:
        print("❌ No se encontraron libros.\n")


def actualizar_libro():
    id_libro = input("Ingrese el ID del libro a actualizar: ")
    libro = session.get(Libro, id_libro)
    if not libro:
        print("⚠️ No existe un libro con ese ID.\n")
        return

    campo = input("Campo a modificar (titulo, autor, genero, leido): ").lower()
    nuevo_valor = input(f"Nuevo valor para {campo}: ")

    try:
        setattr(libro, campo, nuevo_valor)
        session.commit()
        print("✅ Libro actualizado correctamente.\n")
    except Exception as e:
        session.rollback()
        print("❌ Error al actualizar:", e)


def eliminar_libro():
    id_libro = input("Ingrese el ID del libro a eliminar: ")
    libro = session.get(Libro, id_libro)
    if not libro:
        print("⚠️ No existe un libro con ese ID.\n")
        return
    try:
        session.delete(libro)
        session.commit()
        print("🗑️ Libro eliminado correctamente.\n")
    except Exception as e:
        session.rollback()
        print("❌ Error al eliminar libro:", e)


# -----------------------------------------------
# MENÚ PRINCIPAL
# -----------------------------------------------
def menu():
    while True:
        print("""
============== 📖 MENÚ DE BIBLIOTECA (MariaDB) ==============
1. Agregar nuevo libro
2. Ver listado de libros
3. Buscar libros
4. Actualizar información de un libro
5. Eliminar libro existente
6. Salir
=============================================================
""")
        opcion = input("Seleccione una opción (1-6): ")

        if opcion == "1":
            agregar_libro()
        elif opcion == "2":
            ver_libros()
        elif opcion == "3":
            buscar_libro()
        elif opcion == "4":
            actualizar_libro()
        elif opcion == "5":
            eliminar_libro()
        elif opcion == "6":
            print("👋 Saliendo del programa...")
            session.close()
            break
        else:
            print("❌ Opción inválida.\n")


# -----------------------------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------------------------
if __name__ == "__main__":
    menu()
