import sqlite3

conexion = sqlite3.connect("trinidad_reporta.db")
cursor = conexion.cursor()

# =========================
# TABLA BARRIOS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS barrios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
""")

# =========================
# TABLA PROBLEMAS
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS problemas(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
)
""")

# =========================
# TABLA REPORTES
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS reportes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    nombre_ciudadano TEXT NOT NULL,
    barrio_id INTEGER NOT NULL,
    problema_id INTEGER NOT NULL,
    descripcion TEXT NOT NULL,
    imagen TEXT,
    estado TEXT DEFAULT 'Pendiente',
    fecha_reporte TEXT NOT NULL,
    fecha_actualizacion TEXT,

    FOREIGN KEY (barrio_id) REFERENCES barrios(id),
    FOREIGN KEY (problema_id) REFERENCES problemas(id)
)
""")

# =========================
# TABLA ADMINISTRADORES
# =========================
cursor.execute("""
CREATE TABLE IF NOT EXISTS administradores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    contraseña TEXT NOT NULL
)
""")

# =========================
# BARRIOS INICIALES
# =========================
barrios = [
    ("Centro",),
    ("Pompeya",),
    ("El Carmen",),
    ("Villa Corina",),
    ("13 de Abril",),
    ("Pedro Ignacio Muiba",),
    ("San Juan",),
    ("Arroyo Chico",),
    ("Otro",)
]

cursor.executemany("""
INSERT OR IGNORE INTO barrios(nombre)
VALUES(?)
""", barrios)

# =========================
# PROBLEMAS INICIALES
# =========================
problemas = [
    ("Bache",),
    ("Alumbrado Público",),
    ("Alcantarillado",),
    ("Cuneta Dañada",),
    ("Acumulación de Basura",),
    ("Fuga de Agua",),
    ("Inundación",),
    ("Semáforo Dañado",),
    ("Área Verde Deteriorada",),
    ("Otro",)
]

cursor.executemany("""
INSERT OR IGNORE INTO problemas(nombre)
VALUES(?)
""", problemas)

# =========================
# ADMINISTRADOR INICIAL
# =========================
cursor.execute("""
INSERT OR IGNORE INTO administradores(usuario, contraseña)
VALUES('admin','1234')
""")

conexion.commit()
conexion.close()

print("Base de datos creada correctamente.")