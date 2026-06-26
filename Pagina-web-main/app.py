from flask import Flask, request, jsonify
from flask_cors import CORS
# Importamos tu configuración de base de datos existente
from db import get_db_connection 

app = Flask(__name__)
CORS(app)

# ==========================================
# CLASES DE CONTROL PARA EL ADMINISTRADOR
# ==========================================

class AdminTarifas:
    @staticmethod
    def actualizar():
        try:
            datos = request.get_json()
            id_tarifa = datos.get('id')
            nuevo_monto = datos.get('monto')
            
            conexion = get_db_connection()
            cursor = conexion.cursor()
            sql = "UPDATE tarifas SET monto = %s WHERE id = %s"
            cursor.execute(sql, (nuevo_monto, id_tarifa))
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({"status": "success", "mensaje": "Tarifa actualizada con éxito"}), 200
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)}), 500

class AdminChoferes:
    @staticmethod
    def actualizar_padron():
        try:
            datos = request.get_json()
            id_chofer = datos.get('id')
            estado = datos.get('estado')
            
            conexion = get_db_connection()
            cursor = conexion.cursor()
            sql = "UPDATE choferes SET estado = %s WHERE id = %s"
            cursor.execute(sql, (estado, id_chofer))
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({"status": "success", "mensaje": "Padrón de choferes actualizado"}), 200
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)}), 500

class AdminNovedades:
    @staticmethod
    def subir():
        try:
            datos = request.get_json()
            titulo = datos.get('titulo')
            contenido = datos.get('contenido')
            
            conexion = get_db_connection()
            cursor = conexion.cursor()
            sql = "INSERT INTO novedades (titulo, contenido) VALUES (%s, %s)"
            cursor.execute(sql, (titulo, contenido))
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({"status": "success", "mensaje": "Novedad publicada con éxito"}), 201
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)}), 500

    @staticmethod
    def eliminar(id_novedad):
        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()
            sql = "DELETE FROM novedades WHERE id = %s"
            cursor.execute(sql, (id_novedad,))
            conexion.commit()
            cursor.close()
            conexion.close()
            return jsonify({"status": "success", "mensaje": "Novedad eliminada"}), 200
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)}), 500

class AdminQuejas:
    @staticmethod
    def listar_todas():
        try:
            conexion = get_db_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM quejas")
            lista_quejas = cursor.fetchall()
            cursor.close()
            conexion.close()
            return jsonify({"status": "success", "datos": lista_quejas}), 200
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)}), 500

class AdminCarrerasPrivadas:
    @staticmethod
    def listar_todas():
        try:
            conexion = get_db_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM solicitudes_carrera")
            carreras = cursor.fetchall()
            cursor.close()
            conexion.close()
            return jsonify({"status": "success", "datos": carreras}), 200
        except Exception as e:
            return jsonify({"status": "error", "mensaje": str(e)}), 500


# ==========================================
# ENDPOINTS / RUTAS DEL ADMINISTRADOR
# ==========================================

@app.route('/api/admin/tarifas', methods=['PUT'])
def api_admin_tarifas():
    return AdminTarifas.actualizar()

@app.route('/api/admin/choferes', methods=['PUT'])
def api_admin_choferes():
    return AdminChoferes.actualizar_padron()

@app.route('/api/admin/novedades', methods=['POST'])
def api_admin_subir_novedad():
    return AdminNovedades.subir()

@app.route('/api/admin/novedades/<int:id>', methods=['DELETE'])
def api_admin_eliminar_novedad(id):
    return AdminNovedades.eliminar(id)

@app.route('/api/admin/quejas', methods=['GET'])
def api_admin_ver_quejas():
    return AdminQuejas.listar_todas()

@app.route('/api/admin/carreras-privadas', methods=['GET'])
def api_admin_ver_carreras():
    return AdminCarrerasPrivadas.listar_todas()


# ==========================================
# RUTAS DE USUARIOS EXISTENTES
# ==========================================

@app.route('/api/carreras', methods=['POST'])
def solicitar_carrera():
    try:
        datos = request.get_json()
        origen = datos.get('origen')
        destino = datos.get('destino')
        monto = datos.get('monto')

        conexion = get_db_connection()
        cursor = conexion.cursor()
        sql = "INSERT INTO solicitudes_carrera (direccion_origen, direccion_destino, monto_ofrecido) VALUES (%s, %s, %s)"
        cursor.execute(sql, (origen, destino, monto))
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"status": "success", "mensaje": "¡Carrera registrada en la BD!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500

@app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    try:
        datos = request.get_json()
        valores = (datos.get('nombres'), datos.get('apellidos'), datos.get('telefono'), datos.get('correo'), datos.get('password'))

        conexion = get_db_connection()
        cursor = conexion.cursor()
        sql = "INSERT INTO usuarios (nombres, apellidos, telefono, correo, password) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, valores)
        conexion.commit()
        cursor.close()
        conexion.close()
        return jsonify({"status": "success", "mensaje": "¡Usuario creado con éxito!"}), 201
    except Exception as e:
        return jsonify({"status": "error", "mensaje": "El correo ya se encuentra registrado."}), 500

@app.route('/api/login', methods=['POST'])
def iniciar_sesion():
    try:
        datos = request.get_json()
        correo_ingresado = datos.get('usuario')
        password_ingresada = datos.get('password')

        conexion = get_db_connection()
        cursor = conexion.cursor()
        sql = "SELECT id, nombres FROM usuarios WHERE correo = %s AND password = %s"
        cursor.execute(sql, (correo_ingresado, password_ingresada))
        resultado = cursor.fetchone()
        cursor.close()
        conexion.close()

        if resultado:
            return jsonify({"status": "success", "mensaje": f"¡Bienvenido {resultado[1]}!"}), 200
        else:
            return jsonify({"status": "error", "mensaje": "Correo o contraseña incorrectos"}), 401
    except Exception as e:
        return jsonify({"status": "error", "mensaje": str(e)}), 500


# ==========================================
# BLOQUE DE ARRANQUE DEL SERVIDOR
# ==========================================
if __name__ == '__main__':
    print("🚀 ¡Servidor de Hijos de Cristo Rey levantado correctamente!")
    app.run(debug=True, port=5000)