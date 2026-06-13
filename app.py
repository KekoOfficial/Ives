from flask import Flask, render_template, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime

# ---------------- CONFIGURACIÓN ----------------
TOKEN = "8459092113:AAFFJ0b7H5gFzYjgYGk_g_57cI709dhVRhI"
TU_CHAT_ID = "8688232119"
API_TELEGRAM = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

ALCANCE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDENCIALES = ServiceAccountCredentials.from_json_keyfile_name("credenciales_google.json", ALCANCE)
CLIENTE_GOOGLE = gspread.authorize(CREDENCIALES)
HOJA = CLIENTE_GOOGLE.open("Inventario Productos").sheet1

CATEGORIAS = ["Perfume", "Crema", "Maquillaje", "Líquido"]
lista_temporal = []
LIMITE = 10

app = Flask(__name__)

# ---------------- FUNCIONES ----------------
def guardar_en_google(fecha, codigo, tipo):
    HOJA.append_row([fecha, codigo, tipo])

def enviar_lista_telegram(lista):
    texto = "📦 LISTA DE PRODUCTOS (10 unidades)\n" + "━"*40 + "\n"
    for i, item in enumerate(lista, 1):
        texto += f"{i}. Código: {item['codigo']} | Tipo: {item['tipo']} | {item['fecha']}\n"
    texto += "\n✅ Lista enviada - Reiniciando conteo"
    requests.post(API_TELEGRAM, data={"chat_id": TU_CHAT_ID, "text": texto})

# ---------------- RUTAS WEB ----------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    global lista_temporal
    datos = request.get_json()
    codigo = datos.get('codigo', '').strip()
    tipo = datos.get('tipo', '')
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    if not codigo or tipo not in CATEGORIAS:
        return jsonify({"ok": False, "mensaje": "Datos inválidos"})

    guardar_en_google(fecha, codigo, tipo)
    lista_temporal.append({"codigo": codigo, "tipo": tipo, "fecha": fecha})

    if len(lista_temporal) >= LIMITE:
        enviar_lista_telegram(lista_temporal)
        lista_temporal = []
        return jsonify({"ok": True, "mensaje": "✅ Lista completa enviada a Telegram", "contador": 0})

    return jsonify({"ok": True, "mensaje": "✅ Registrado correctamente", "contador": len(lista_temporal)})

# ---------------- INICIO ----------------
if __name__ == '__main__':
    print("✅ Sistema corriendo en: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
