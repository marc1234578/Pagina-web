from flask import Flask, request, jsonify
from flask_cors import CORS

# 🌟 Importamos tu nueva configuración de base de datos
from db import get_db_connection 

app = Flask(__name__)
CORS(app)

@app.route('/api/quejas', methods=['POST'])
def registrar_queja():
    try:
        datos = request.get_json()
        
        nombre = datos.get('nombre')
        correo = datos.get('correo')
        detalle = datos.get('detalle')

        # Usamos la función importada desde db.py
        conexion = get_db_connection()
        cursor = conexion.cursor()

        sql = "INSERT INTO reportes_ayuda (nombre_completo, correo_contacto, detalle_queja) VALUES (%s, %s, %s)"
        valores = (nombre, correo, detalle)
        
        cursor.execute(sql, valores)
        conexion.commit()

        cursor.close()
        conexion.close()

        return jsonify({"status": "success", "mensaje": "¡Reporte guardado!"}), 201

    except Exception as e:
        print("ERROR EN PYTHON:", str(e))
        return jsonify({"status": "error", "mensaje": str(e)}), 500

if __name__ == '__main__':
    print("Iniciando servidor de Hijos de Cristo Rey...")
    app.run(debug=True, port=5000)