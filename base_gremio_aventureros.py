import sqlite3

# Crear (o conectar a) la base de datos
conexion = sqlite3.connect("gremio_aventureros.db")
cursor = conexion.cursor()

# -----------------------------------------------------
# Crear tabla de héroes
# -----------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    clase TEXT CHECK(clase IN ('Guerrero', 'Mago', 'Arquero', 'Ladrón', 'Paladín', 'Hechicero')) NOT NULL,
    nivel_experiencia INTEGER CHECK(nivel_experiencia >= 1) NOT NULL
);
""")

# -----------------------------------------------------
# Crear tabla de misiones
# -----------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS misiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    dificultad TEXT CHECK(dificultad IN ('Fácil', 'Media', 'Difícil', 'Épica')) NOT NULL,
    localizacion TEXT NOT NULL,
    recompensa INTEGER CHECK(recompensa >= 0) NOT NULL
);
""")

# -----------------------------------------------------
# Crear tabla de monstruos
# -----------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS monstruos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT CHECK(tipo IN ('Dragón', 'Goblin', 'No-muerto', 'Bestia', 'Humanoide', 'Demonio')) NOT NULL,
    nivel_amenaza INTEGER CHECK(nivel_amenaza BETWEEN 1 AND 10) NOT NULL
);
""")

# -----------------------------------------------------
# Tabla relacional misiones_heroes (Muchos a Muchos)
# -----------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS misiones_heroes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_heroe INTEGER NOT NULL,
    id_mision INTEGER NOT NULL,
    FOREIGN KEY (id_heroe) REFERENCES heroes(id) ON DELETE CASCADE,
    FOREIGN KEY (id_mision) REFERENCES misiones(id) ON DELETE CASCADE,
    UNIQUE(id_heroe, id_mision)
);
""")

# -----------------------------------------------------
# Tabla relacional misiones_monstruos (Muchos a Muchos)
# -----------------------------------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS misiones_monstruos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_mision INTEGER NOT NULL,
    id_monstruo INTEGER NOT NULL,
    FOREIGN KEY (id_mision) REFERENCES misiones(id) ON DELETE CASCADE,
    FOREIGN KEY (id_monstruo) REFERENCES monstruos(id) ON DELETE CASCADE,
    UNIQUE(id_mision, id_monstruo)
);
""")

# -----------------------------------------------------
# Confirmar cambios y cerrar conexión
# -----------------------------------------------------
conexion.commit()
conexion.close()

print("✅ Base de datos 'gremio_aventureros.db' creada exitosamente.")
