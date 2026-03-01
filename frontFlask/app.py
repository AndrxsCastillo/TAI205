from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# La URL de tu API en Docker (según tu captura es el puerto 5000)
API_URL = "http://localhost:5000/v1/usuarios/"

@app.route('/')
def index():
    # GET: Consultar todos los usuarios para la tabla
    response = requests.get(API_URL)
    data = response.json()
    # Pasamos la lista de usuarios al HTML
    return render_template('index.html', usuarios=data.get('data', []))

@app.route('/agregar', methods=['POST'])
def agregar():
    # POST: Recibir datos del formulario y enviarlos a FastAPI
    nuevo_usuario = {
        "id": request.form['id'],
        "nombre": request.form['nombre'],
        "edad": request.form['edad']
    }
    requests.post(API_URL, json=nuevo_usuario)
    return redirect(url_for('index'))

@app.route('/eliminar/<id>')
def eliminar(id):
    # DELETE: Llamar al endpoint de eliminación
    requests.delete(f"{API_URL}{id}")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) # Corremos Flask en el 5001 para que no choque con la API