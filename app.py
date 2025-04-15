from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import qrcode
import io
from datetime import datetime

app = Flask(__name__)
NOMBRE_MEDICO = "Dr. Juan Pérez"

# Base de datos
def init_db():
    conn = sqlite3.connect('vacunacion.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS carnet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha TEXT NOT NULL,
            medico TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('formulario.html', medico=NOMBRE_MEDICO)

@app.route('/guardar', methods=['POST'])
def guardar():
    nombre = request.form['nombre'].strip()
    fecha = request.form['fecha'].strip()

    # Validación
    try:
        fecha_obj = datetime.strptime(fecha, "%d/%m/%Y")
        if fecha_obj > datetime.now():
            return "❌ Fecha inválida: no puede ser futura."
    except ValueError:
        return "❌ Formato de fecha inválido. Usa dd/mm/aaaa."

    if not nombre.replace(" ", "").isalpha():
        return "❌ Nombre inválido. Usa solo letras."

    # Guardar en base de datos
    conn = sqlite3.connect('vacunacion.db')
    c = conn.cursor()
    c.execute("INSERT INTO carnet (nombre, fecha, medico) VALUES (?, ?, ?)", (nombre, fecha, NOMBRE_MEDICO))
    conn.commit()
    conn.close()

    return redirect(f"/ver/{nombre}")

@app.route('/ver/<nombre>')
def ver(nombre):
    conn = sqlite3.connect('vacunacion.db')
    c = conn.cursor()
    c.execute("SELECT * FROM carnet WHERE nombre = ?", (nombre,))
    datos = c.fetchone()
    conn.close()

    if datos:
        return render_template('ver_carnet.html', datos=datos)
    else:
        return "❌ Paciente no encontrado."

@app.route('/qr/<nombre>')
def qr(nombre):
    conn = sqlite3.connect('vacunacion.db')
    c = conn.cursor()
    c.execute("SELECT * FROM carnet WHERE nombre = ?", (nombre,))
    datos = c.fetchone()
    conn.close()

    if not datos:
        return "❌ No encontrado."

    _, nombre, fecha, medico = datos
    contenido = f"Paciente: {nombre}\nFecha: {fecha}\nMédico: {medico}"

    img = qrcode.make(contenido)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
