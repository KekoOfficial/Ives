from flask import Flask, request, jsonify
import requests
from datetime import datetime
from config import API_TELEGRAM, TU_CHAT_ID, CATEGORIAS, LIMITE

app = Flask(__name__)
lista_temporal = []

def guardar_local(fecha, codigo, tipo):
    with open("inventario.txt", "a", encoding="utf-8") as f:
        f.write(f"{fecha} | {codigo} | {tipo}\n")

def enviar_lista(lista):
    texto = "📦 LISTA DE PRODUCTOS (10 unidades)\n"
    texto += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    for i, item in enumerate(lista, 1):
        texto += f"{i}. Código: {item['codigo']} | Tipo: {item['tipo']} | {item['fecha']}\n"
    texto += "\n✅ Lista enviada, conteo reiniciado"
    requests.post(API_TELEGRAM, data={"chat_id": TU_CHAT_ID, "text": texto})

@app.route('/')
def inicio():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.route('/estilos.css')
def css():
    with open("estilos.css", "r", encoding="utf-8") as f:
        return f.read(), 200, {'Content-Type': 'text/css'}

@app.route('/registrar', methods=['POST'])
def registrar():
    global lista_temporal
    datos = request.get_json()
    codigo = datos.get("codigo", "").strip()
    tipo = datos.get("tipo", "")
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    if not codigo or tipo not in CATEGORIAS:
        return jsonify({"ok": False, "mensaje": "Datos inválidos"})

    guardar_local(fecha, codigo, tipo)
    lista_temporal.append({"codigo": codigo, "tipo": tipo, "fecha": fecha})

    if len(lista_temporal) >= LIMITE:
        enviar_lista(lista_temporal)
        lista_temporal = []
        return jsonify({"ok": True, "mensaje": "✅ Lista enviada a Telegram", "contador": 0})

    return jsonify({"ok": True, "mensaje": "✅ Registrado correctamente", "contador": len(lista_temporal)})

if __name__ == '__main__':
    # Usamos 0.0.0.0 para que el navegador tome mejor los permisos
    print("✅ Abre en: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
