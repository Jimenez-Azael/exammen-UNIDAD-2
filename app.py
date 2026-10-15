
from datetime import date, datetime

import requests
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

FECHA_INICIO = date(2026, 1, 1)
FECHA_FIN = date(2026, 10, 14)

URL_API = "https://api.frankfurter.dev/v2/rates"


@app.get("/")
def inicio():
    return render_template(
        "index.html",
        mensaje="API del precio historico del dolar",
        moneda_origen="USD",
        moneda_destino="MXN",
        fecha_inicio=str(FECHA_INICIO),
        fecha_fin=str(FECHA_FIN),
        ejemplo="/api/dolar?fecha=2026-03-15"
    )


@app.get("/api/dolar")
def consultar_dolar():
    fecha_texto = request.args.get("fecha")

    if not fecha_texto:
        return jsonify({
            "error": "Debes indicar una fecha.",
            "ejemplo": "/api/dolar?fecha=2026-03-15"
        }), 400

    try:
        fecha = datetime.strptime(
            fecha_texto, "%Y-%m-%d"
        ).date()
    except ValueError:
        return jsonify({
            "error": "Formato incorrecto. Usa AAAA-MM-DD."
        }), 400

    if not FECHA_INICIO <= fecha <= FECHA_FIN:
        return jsonify({
            "error": "La fecha debe estar entre "
                     "2026-01-01 y 2026-10-14."
        }), 400

    try:
        respuesta = requests.get(
            URL_API,
            params={
                "date": str(fecha),
                "base": "USD",
                "quotes": "MXN"
            },
            timeout=15
        )
        respuesta.raise_for_status()
        datos = respuesta.json()

    except requests.RequestException:
        return jsonify({
            "error": "No se pudo consultar el servicio "
                     "de tipos de cambio."
        }), 502

    if not datos:
        return jsonify({
            "error": "No hay una cotizacion disponible "
                     "para esa fecha."
        }), 404

    cotizacion = next(
        (dato for dato in datos if dato.get("quote") == "MXN"),
        None
    )

    if cotizacion is None:
        return jsonify({
            "error": "No se encontro el tipo de cambio MXN."
        }), 404

    return jsonify({
        "fecha_solicitada": str(fecha),
        "fecha_cotizacion": cotizacion["date"],
        "par": "USD/MXN",
        "precio_en_pesos_por_dolar": cotizacion["rate"],
        "fuente": "BANXICO"
    })


if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5000, debug=True)
     