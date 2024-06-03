from OPC_CLIENT import *
from EQUIPO import * 
from config import *
from apscheduler.schedulers.background import BackgroundScheduler

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin

app = Flask(__name__) 
CORS(app)

SUSCRIBIR=1
LECTURA=2
"""
-----------------------------------
"""

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', seconds=TIME_INTERVAL, max_instances=1)
def job():
    try:
        with app.app_context():
            cliente1.leer_nodos()
            estado_EQ1 = cliente1.get_nodo_value(equipo1.obtener_id_nombre("ESTADO"))
            equipo1.cambiar_estado(estado_EQ1)
            equipo1.guardar_valores_sensores()
            
    except Exception as e:
        print(f"Error al interactuar con Equipo 1: {e}")
        print("Equipo no disponible")

# Routes
@cross_origin
@app.route('/Reporte/<equipo>', methods=['GET'])
def consultar_datos(equipo):
    try:
        json_data = {}
        if equipo == equipo1.nombre:  
            json_data = equipo1.report_datos()
        return json_data
        
    except Exception as e:
        return jsonify({"error": f"Error al consultar datos: {str(e)}"}), 500

@cross_origin
@app.route('/Historico/<equipo>/<tag>', methods=['GET'])
def consultar_historicos(equipo, tag):
    try:
        json_data = {}

        if equipo == equipo1.nombre:  
            json_data = equipo1.reporte_sensor(tag)
        return json_data

    except Exception as e:
        return jsonify({"error": f"Error al consultar datos: {str(e)}"}), 500
    
@cross_origin
@app.route('/home', methods=['GET'])
def consultar_home():
    try:
        json_data = {}    
        for equipo in equipos:
            json_data.update(equipo.reporte_home())
        return jsonify(json_data), 200

    except Exception as e:
        return jsonify({"error": f"Error al consultar datos: {str(e)}"}), 500



equipos=[]


if __name__ == '__main__':
    try:
        cliente1 = Cliente_OPC("PLC1", URL, NS)
        for nodo in nodos1:
            cliente1.agregar_nodo(nodo[0])

        equipo1 = Equipo("Cocina1", 1, cliente1)
        for nodo in nodos1:
            equipo1.agregar_sensor(nodo[0], nodo[1])

        cliente1.conectar()
        equipos.append(equipo1)

        # Inicio de lectura del cliente y del equipo 
        scheduler.start()
        app.run(host=IP, debug=False, use_reloader=False, port=5001)

    except KeyboardInterrupt:
        print("desconectando")
        cliente1.desconectar()
    finally:
        print("desconectando")
        cliente1.desconectar()
