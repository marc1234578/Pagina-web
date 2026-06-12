from flask import Flask, request, jsonify
from flask_cors import CORS

# 🌟 Importamos tu nueva configuración de base de datos
from db import get_db_connection 

app = Flask(__name__)
CORS(app)

@app.route('/api/carreras', methods=['POST'])
def solicitar_carrera():
    try:
        datos = request.get_json()
        
        # Capturamos los 3 datos que manda el HTML
        origen = datos.get('origen')
        destino = datos.get('destino')
        monto = datos.get('monto')

        print(f"🚕 Nueva carrera recibida: {origen} -> {destino} (S/ {monto})")

        # Conexión a la BD usando db.py
        conexion = get_db_connection()
        cursor = conexion.cursor()

        # Insertamos en la nueva tabla que creaste en SQL
        sql = "INSERT INTO solicitudes_carrera (direccion_origen, direccion_destino, monto_ofrecido) VALUES (%s, %s, %s)"
        valores = (origen, destino, monto)
        
        cursor.execute(sql, valores)
        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({"status": "success", "mensaje": "¡Carrera registrada en la BD!"}), 201

    except Exception as e:
        print("ERROR EN PYTHON:", str(e))
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == '__main__':
    print("Iniciando servidor de Hijos de Cristo Rey...")
    app.run(debug=True, port=5000)