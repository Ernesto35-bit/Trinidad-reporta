from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "trinidad_reporta_2026"
# Carpeta donde se guardarán las imágenes
CARPETA_IMAGENES = "static/imagenes"

if not os.path.exists(CARPETA_IMAGENES):
    os.makedirs(CARPETA_IMAGENES)

# =========================
# PÁGINA PRINCIPAL
# =========================
@app.route("/", methods=["GET", "POST"])
def inicio():

    conexion = sqlite3.connect("trinidad_reporta.db")
    cursor = conexion.cursor()

    mensaje = ""
    codigo = ""
    fecha_reporte = ""

    if request.method == "POST":

        nombre = request.form["nombre"]
        barrio_id = request.form["barrio"]
        problema_id = request.form["problema"]
        descripcion = request.form["descripcion"]
        imagen = request.files["imagen"]
        nombre_imagen = ""

        if imagen and imagen.filename != "":

            nombre_imagen = secure_filename(imagen.filename)

            ruta = os.path.join(CARPETA_IMAGENES, nombre_imagen)

            imagen.save(ruta)

        cursor.execute("SELECT MAX(id) FROM reportes")
        ultimo_id = cursor.fetchone()[0]

        if ultimo_id is None:
            nuevo_numero = 1
        else:
            nuevo_numero = ultimo_id + 1

        codigo = f"TR-{nuevo_numero:05d}"

        fecha_reporte = datetime.now().strftime("%d/%m/%Y %H:%M")

        cursor.execute("""
        INSERT INTO reportes(
            codigo,
            nombre_ciudadano,
            barrio_id,
            problema_id,
            descripcion,
            imagen,
            estado,
            fecha_reporte
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            codigo,
            nombre,
            barrio_id,
            problema_id,
            descripcion,
            nombre_imagen,
            "Pendiente",
            fecha_reporte
        ))

        conexion.commit()

        mensaje = "Reporte registrado correctamente."

    cursor.execute("SELECT * FROM barrios")
    barrios = cursor.fetchall()

    cursor.execute("SELECT * FROM problemas")
    problemas = cursor.fetchall()

    conexion.close()

    return render_template(
        "index.html",
        barrios=barrios,
        problemas=problemas,
        mensaje=mensaje,
        codigo=codigo,
        fecha=fecha_reporte
    )


# =========================
# CONSULTAR REPORTE
# =========================
@app.route("/consultar", methods=["GET", "POST"])
def consultar():

    conexion = sqlite3.connect("trinidad_reporta.db")
    cursor = conexion.cursor()

    reporte = None
    mensaje = ""

    if request.method == "POST":

        codigo = request.form["codigo"]

        cursor.execute("""
        SELECT
            reportes.codigo,
            reportes.nombre_ciudadano,
            barrios.nombre,
            problemas.nombre,
            reportes.descripcion,
            reportes.estado,
            reportes.fecha_reporte
        FROM reportes
        INNER JOIN barrios
            ON reportes.barrio_id = barrios.id
        INNER JOIN problemas
            ON reportes.problema_id = problemas.id
        WHERE reportes.codigo = ?
        """, (codigo,))

        reporte = cursor.fetchone()

        if reporte is None:
            mensaje = "No existe un reporte con ese código."

    conexion.close()

    return render_template(
        "consultar.html",
        reporte=reporte,
        mensaje=mensaje
    )

# =========================
# LOGIN ADMINISTRADOR
# =========================
@app.route("/admin", methods=["GET", "POST"])
def admin():

    conexion = sqlite3.connect("trinidad_reporta.db")
    cursor = conexion.cursor()

    mensaje = ""

    if request.method == "POST":

        usuario = request.form["usuario"]
        contraseña = request.form["contraseña"]

        cursor.execute("""
        SELECT *
        FROM administradores
        WHERE usuario = ? AND contraseña = ?
        """, (usuario, contraseña))

        administrador = cursor.fetchone()

        if administrador:

            session["admin"] = usuario

            conexion.close()

            return redirect(url_for("panel_admin"))

        else:

            mensaje = "Usuario o contraseña incorrectos."

    conexion.close()

    return render_template(
        "login_admin.html",
        mensaje=mensaje
    )
# =========================
# PANEL ADMINISTRADOR
# =========================
@app.route("/panel_admin")
def panel_admin():

    if "admin" not in session:
        return redirect(url_for("admin"))

    conexion = sqlite3.connect("trinidad_reporta.db")
    cursor = conexion.cursor()

    # =========================
    # ESTADÍSTICAS
    # =========================
    cursor.execute("SELECT COUNT(*) FROM reportes")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reportes WHERE estado='Pendiente'")
    pendientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reportes WHERE estado='En proceso'")
    proceso = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reportes WHERE estado='Resuelto'")
    resueltos = cursor.fetchone()[0]

    # =========================
    # LISTA DE REPORTES
    # =========================
    cursor.execute("""
    SELECT
        reportes.id,
        reportes.codigo,
        reportes.nombre_ciudadano,
        barrios.nombre,
        problemas.nombre,
        reportes.imagen,
        reportes.estado,
        reportes.fecha_reporte
    FROM reportes

    INNER JOIN barrios
        ON reportes.barrio_id = barrios.id

    INNER JOIN problemas
        ON reportes.problema_id = problemas.id

    ORDER BY reportes.id DESC
    """)

    reportes = cursor.fetchall()
    print(reportes)
    conexion.close()

    return render_template(
        "panel_admin.html",
        reportes=reportes,
        total=total,
        pendientes=pendientes,
        proceso=proceso,
        resueltos=resueltos
    )
# =========================
# EDITAR REPORTE
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar_reporte(id):

    if "admin" not in session:
        return redirect(url_for("admin"))

    conexion = sqlite3.connect("trinidad_reporta.db")
    cursor = conexion.cursor()

    if request.method == "POST":

        estado = request.form["estado"]

        fecha_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M")

        cursor.execute("""
        UPDATE reportes
        SET estado = ?,
            fecha_actualizacion = ?
        WHERE id = ?
        """, (
            estado,
            fecha_actualizacion,
            id
        ))

        conexion.commit()
        conexion.close()

        return redirect(url_for("panel_admin"))

    cursor.execute("""
    SELECT
        reportes.id,
        reportes.codigo,
        reportes.nombre_ciudadano,
        barrios.nombre,
        problemas.nombre,
        reportes.descripcion,
        reportes.imagen,
        reportes.estado,
        reportes.fecha_reporte
    FROM reportes

    INNER JOIN barrios
        ON reportes.barrio_id = barrios.id

    INNER JOIN problemas
        ON reportes.problema_id = problemas.id

    WHERE reportes.id = ?
    """, (id,))

    reporte = cursor.fetchone()

    conexion.close()

    return render_template(
        "editar_reporte.html",
        reporte=reporte
    )
# =========================
# CONFIGURACIÓN
# =========================
@app.route("/configuracion", methods=["GET", "POST"])
def configuracion():

    if "admin" not in session:
        return redirect(url_for("admin"))

    conexion = sqlite3.connect("trinidad_reporta.db")
    cursor = conexion.cursor()

    mensaje = ""

    cursor.execute("""
    SELECT id, usuario
    FROM administradores
    LIMIT 1
    """)

    administrador = cursor.fetchone()

    if request.method == "POST":

        usuario_actual = request.form["usuario_actual"]
        nuevo_usuario = request.form["nuevo_usuario"]

        contraseña_actual = request.form["contraseña_actual"]
        nueva_contraseña = request.form["nueva_contraseña"]

        cursor.execute("""
        SELECT *
        FROM administradores
        WHERE usuario = ? AND contraseña = ?
        """, (
            usuario_actual,
            contraseña_actual
        ))

        existe = cursor.fetchone()

        if existe:

            cursor.execute("""
            UPDATE administradores
            SET usuario = ?,
                contraseña = ?
            WHERE id = ?
            """, (
                nuevo_usuario,
                nueva_contraseña,
                existe[0]
            ))

            conexion.commit()

            session["admin"] = nuevo_usuario

            administrador = (existe[0], nuevo_usuario)

            mensaje = "Datos actualizados correctamente."

        else:

            mensaje = "Usuario o contraseña actual incorrectos."

    conexion.close()

    return render_template(
        "configuracion.html",
        administrador=administrador,
        mensaje=mensaje
    )
# =========================
# ACERCA DE
# =========================
@app.route("/acerca")
def acerca():

    return render_template("acerca.html")
# =========================
# CERRAR SESIÓN
# =========================
@app.route("/logout")
def logout():

    session.pop("admin", None)

    return redirect(url_for("inicio"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)