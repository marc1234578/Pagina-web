from datetime import date, datetime
from decimal import Decimal

from flask import Flask, request, jsonify
from flask_cors import CORS
from mysql.connector import Error

from db import get_db_connection

app = Flask(__name__)
CORS(app)

ADMIN_EMAILS = {
    'marco@gmail.com',
    'fabrizzio@gmail.com',
    'juan@gmail.com',
    'marcos@gmail.com',
}


def normalizar_valor(valor):
    """Convierte fechas y decimales de MySQL para que Flask pueda enviarlos como JSON."""
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    return valor


def normalizar_filas(filas):
    return [{clave: normalizar_valor(valor) for clave, valor in fila.items()} for fila in filas]


def respuesta_ok(datos=None, mensaje='Operación realizada correctamente', status_code=200):
    payload = {'status': 'success', 'mensaje': mensaje}
    if datos is not None:
        payload['datos'] = datos
    return jsonify(payload), status_code


def respuesta_error(mensaje='No se pudo completar la operación', status_code=500):
    return jsonify({'status': 'error', 'mensaje': mensaje}), status_code


def ejecutar_select(sql, params=None, uno=False):
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        resultado = cursor.fetchone() if uno else cursor.fetchall()
        if uno:
            return resultado
        return normalizar_filas(resultado)
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def ejecutar_cambio(sql, params=None):
    conexion = None
    cursor = None
    try:
        conexion = get_db_connection()
        cursor = conexion.cursor()
        cursor.execute(sql, params or ())
        conexion.commit()
        return cursor.rowcount, cursor.lastrowid
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def texto_obligatorio(datos, campo, nombre=None):
    valor = str(datos.get(campo, '')).strip()
    if not valor:
        raise ValueError(f'El campo {nombre or campo} es obligatorio.')
    return valor


# ==========================================
# ENDPOINTS PÚBLICOS / CLIENTES
# ==========================================

@app.route('/api/registrar', methods=['POST'])
def registrar_usuario():
    try:
        datos = request.get_json() or {}
        nombres = texto_obligatorio(datos, 'nombres', 'nombres')
        apellidos = texto_obligatorio(datos, 'apellidos', 'apellidos')
        telefono = texto_obligatorio(datos, 'telefono', 'teléfono')
        correo = texto_obligatorio(datos, 'correo', 'correo').lower()
        password = texto_obligatorio(datos, 'password', 'contraseña')

        sql = """
            INSERT INTO usuarios (nombres, apellidos, telefono, correo, password)
            VALUES (%s, %s, %s, %s, %s)
        """
        ejecutar_cambio(sql, (nombres, apellidos, telefono, correo, password))
        return respuesta_ok(mensaje='¡Usuario creado con éxito!', status_code=201)
    except Error as e:
        if getattr(e, 'errno', None) == 1062:
            return respuesta_error('El correo ya se encuentra registrado.', 409)
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/login', methods=['POST'])
def iniciar_sesion():
    try:
        datos = request.get_json() or {}
        correo = texto_obligatorio(datos, 'usuario', 'correo').lower()
        password = texto_obligatorio(datos, 'password', 'contraseña')

        usuario = ejecutar_select(
            "SELECT id, nombres, apellidos, correo FROM usuarios WHERE correo = %s AND password = %s LIMIT 1",
            (correo, password),
            uno=True,
        )
        if usuario:
            tipo = 'admin' if correo in ADMIN_EMAILS else 'usuario'
            return respuesta_ok({
                'id': usuario['id'],
                'nombre': usuario['nombres'],
                'tipo': tipo,
                'correo': usuario['correo'],
            }, f"¡Bienvenido {usuario['nombres']}!")

        # Los conductores tienen su propio acceso, pero usan el mismo formulario de inicio.
        chofer = ejecutar_select(
            """
            SELECT id, nombres, apellidos, correo, placa, estado
            FROM choferes
            WHERE correo = %s AND password = %s
            LIMIT 1
            """,
            (correo, password),
            uno=True,
        )
        if chofer:
            if chofer.get('estado') == 'Suspendido':
                return respuesta_error('Tu acceso está suspendido. Comunícate con administración.', 403)
            return respuesta_ok({
                'id': chofer['id'],
                'nombre': chofer['nombres'],
                'tipo': 'conductor',
                'correo': chofer['correo'],
                'placa': chofer.get('placa'),
            }, f"¡Bienvenido conductor {chofer['nombres']}!")

        return respuesta_error('Correo o contraseña incorrectos.', 401)
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/carreras', methods=['POST'])
def solicitar_carrera():
    try:
        datos = request.get_json() or {}
        origen = texto_obligatorio(datos, 'origen', 'origen')
        destino = texto_obligatorio(datos, 'destino', 'destino')
        monto = datos.get('monto')
        if monto in (None, ''):
            raise ValueError('El campo monto es obligatorio.')

        nombre_cliente = str(datos.get('nombre_cliente', '')).strip() or None
        telefono_cliente = str(datos.get('telefono_cliente', '')).strip() or None

        sql = """
            INSERT INTO solicitudes_carrera
            (nombre_cliente, telefono_cliente, direccion_origen, direccion_destino, monto_ofrecido, estado_solicitud)
            VALUES (%s, %s, %s, %s, %s, 'Pendiente')
        """
        ejecutar_cambio(sql, (nombre_cliente, telefono_cliente, origen, destino, monto))
        return respuesta_ok(mensaje='¡Carrera registrada correctamente!', status_code=201)
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/quejas', methods=['POST'])
def registrar_queja():
    try:
        datos = request.get_json() or {}
        nombre = texto_obligatorio(datos, 'nombre', 'nombre')
        correo = texto_obligatorio(datos, 'correo', 'correo')
        detalle = texto_obligatorio(datos, 'detalle', 'detalle')

        sql = """
            INSERT INTO reportes_ayuda (nombre_completo, correo_contacto, detalle_queja, estado_reporte)
            VALUES (%s, %s, %s, 'Pendiente')
        """
        ejecutar_cambio(sql, (nombre, correo, detalle))
        return respuesta_ok(mensaje='Reporte enviado correctamente.', status_code=201)
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/choferes', methods=['GET'])
def listar_choferes_publico():
    try:
        sql = """
            SELECT id, CONCAT(nombres, ' ', apellidos) AS nombre, placa, telefono AS cel, estado
            FROM choferes
            WHERE estado = 'Activo'
            ORDER BY nombres, apellidos
        """
        return respuesta_ok(ejecutar_select(sql), 'Choferes cargados correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/tarifas', methods=['GET'])
def listar_tarifas_publico():
    try:
        sql = """
            SELECT id, tramo, tipo_ruta, adulto, escolar, estado
            FROM tarifas
            WHERE estado = 'Activo'
            ORDER BY FIELD(tipo_ruta, 'Bajada', 'Subida'), id
        """
        return respuesta_ok(ejecutar_select(sql), 'Tarifas cargadas correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/novedades', methods=['GET'])
def listar_novedades_publico():
    try:
        sql = """
            SELECT id, titulo, contenido, fecha_publicacion
            FROM novedades
            ORDER BY fecha_publicacion DESC, id DESC
        """
        return respuesta_ok(ejecutar_select(sql), 'Novedades cargadas correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


# ==========================================
# ENDPOINTS DEL ADMINISTRADOR
# ==========================================

@app.route('/api/admin/resumen', methods=['GET'])
def admin_resumen():
    try:
        datos = {
            'choferes': ejecutar_select("SELECT COUNT(*) AS total FROM choferes", uno=True)['total'],
            'tarifas': ejecutar_select("SELECT COUNT(*) AS total FROM tarifas", uno=True)['total'],
            'quejas_pendientes': ejecutar_select("SELECT COUNT(*) AS total FROM reportes_ayuda WHERE estado_reporte = 'Pendiente'", uno=True)['total'],
            'carreras_pendientes': ejecutar_select("SELECT COUNT(*) AS total FROM solicitudes_carrera WHERE estado_solicitud = 'Pendiente'", uno=True)['total'],
            'novedades': ejecutar_select("SELECT COUNT(*) AS total FROM novedades", uno=True)['total'],
        }
        return respuesta_ok(datos, 'Resumen administrativo cargado.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/tarifas', methods=['GET'])
def admin_listar_tarifas():
    try:
        sql = """
            SELECT id, tramo, tipo_ruta, adulto, escolar, estado
            FROM tarifas
            ORDER BY FIELD(tipo_ruta, 'Bajada', 'Subida'), id
        """
        return respuesta_ok(ejecutar_select(sql), 'Tarifas cargadas correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/tarifas', methods=['POST'])
def admin_crear_tarifa():
    try:
        datos = request.get_json() or {}
        tramo = texto_obligatorio(datos, 'tramo', 'tramo')
        tipo_ruta = texto_obligatorio(datos, 'tipo_ruta', 'tipo de ruta')
        adulto = datos.get('adulto')
        escolar = datos.get('escolar')
        if adulto in (None, '') or escolar in (None, ''):
            raise ValueError('Los montos adulto y escolar son obligatorios.')
        ejecutar_cambio(
            "INSERT INTO tarifas (tramo, tipo_ruta, adulto, escolar, estado) VALUES (%s, %s, %s, %s, 'Activo')",
            (tramo, tipo_ruta, adulto, escolar),
        )
        return respuesta_ok(mensaje='Tarifa creada correctamente.', status_code=201)
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/admin/tarifas', methods=['PUT'])
@app.route('/api/admin/tarifas/<int:id_tarifa>', methods=['PUT'])
def admin_actualizar_tarifa(id_tarifa=None):
    try:
        datos = request.get_json() or {}
        id_tarifa = id_tarifa or datos.get('id')
        if not id_tarifa:
            raise ValueError('No se recibió la tarifa a actualizar.')

        # Compatibilidad con el formulario anterior: {id, monto}
        if 'monto' in datos and 'adulto' not in datos:
            ejecutar_cambio("UPDATE tarifas SET adulto = %s WHERE id = %s", (datos.get('monto'), id_tarifa))
        else:
            tramo = texto_obligatorio(datos, 'tramo', 'tramo')
            tipo_ruta = texto_obligatorio(datos, 'tipo_ruta', 'tipo de ruta')
            adulto = datos.get('adulto')
            escolar = datos.get('escolar')
            estado = str(datos.get('estado', 'Activo')).strip() or 'Activo'
            ejecutar_cambio(
                "UPDATE tarifas SET tramo = %s, tipo_ruta = %s, adulto = %s, escolar = %s, estado = %s WHERE id = %s",
                (tramo, tipo_ruta, adulto, escolar, estado, id_tarifa),
            )
        return respuesta_ok(mensaje='Tarifa actualizada con éxito.')
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/admin/tarifas/<int:id_tarifa>', methods=['DELETE'])
def admin_eliminar_tarifa(id_tarifa):
    try:
        ejecutar_cambio("DELETE FROM tarifas WHERE id = %s", (id_tarifa,))
        return respuesta_ok(mensaje='Tarifa eliminada correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/choferes', methods=['GET'])
def admin_listar_choferes():
    try:
        sql = """
            SELECT id, nombres, apellidos, telefono, correo, placa, licencia, vehiculo, estado, fecha_registro
            FROM choferes
            ORDER BY id DESC
        """
        return respuesta_ok(ejecutar_select(sql), 'Padrón de choferes cargado.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/choferes', methods=['POST'])
def admin_crear_chofer():
    try:
        datos = request.get_json() or {}
        valores = (
            texto_obligatorio(datos, 'nombres', 'nombres'),
            texto_obligatorio(datos, 'apellidos', 'apellidos'),
            texto_obligatorio(datos, 'telefono', 'teléfono'),
            texto_obligatorio(datos, 'correo', 'correo').lower(),
            datos.get('password') or '123456',
            texto_obligatorio(datos, 'placa', 'placa'),
            str(datos.get('licencia', '')).strip() or None,
            str(datos.get('vehiculo', '')).strip() or None,
            str(datos.get('estado', 'Activo')).strip() or 'Activo',
        )
        sql = """
            INSERT INTO choferes (nombres, apellidos, telefono, correo, password, placa, licencia, vehiculo, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        ejecutar_cambio(sql, valores)
        return respuesta_ok(mensaje='Chofer registrado correctamente.', status_code=201)
    except Error as e:
        if getattr(e, 'errno', None) == 1062:
            return respuesta_error('Ya existe un chofer con ese correo o placa.', 409)
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/admin/choferes', methods=['PUT'])
@app.route('/api/admin/choferes/<int:id_chofer>', methods=['PUT'])
def admin_actualizar_chofer(id_chofer=None):
    try:
        datos = request.get_json() or {}
        id_chofer = id_chofer or datos.get('id')
        if not id_chofer:
            raise ValueError('No se recibió el chofer a actualizar.')

        # Compatibilidad con el formulario anterior: {id, estado}
        if set(datos.keys()).issubset({'id', 'estado'}):
            estado = texto_obligatorio(datos, 'estado', 'estado')
            ejecutar_cambio("UPDATE choferes SET estado = %s WHERE id = %s", (estado, id_chofer))
        else:
            valores = (
                texto_obligatorio(datos, 'nombres', 'nombres'),
                texto_obligatorio(datos, 'apellidos', 'apellidos'),
                texto_obligatorio(datos, 'telefono', 'teléfono'),
                texto_obligatorio(datos, 'correo', 'correo').lower(),
                texto_obligatorio(datos, 'placa', 'placa'),
                str(datos.get('licencia', '')).strip() or None,
                str(datos.get('vehiculo', '')).strip() or None,
                str(datos.get('estado', 'Activo')).strip() or 'Activo',
                id_chofer,
            )
            ejecutar_cambio(
                """
                UPDATE choferes
                SET nombres = %s, apellidos = %s, telefono = %s, correo = %s,
                    placa = %s, licencia = %s, vehiculo = %s, estado = %s
                WHERE id = %s
                """,
                valores,
            )
        return respuesta_ok(mensaje='Padrón de choferes actualizado.')
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/admin/choferes/<int:id_chofer>', methods=['DELETE'])
def admin_eliminar_chofer(id_chofer):
    try:
        ejecutar_cambio("DELETE FROM choferes WHERE id = %s", (id_chofer,))
        return respuesta_ok(mensaje='Chofer eliminado correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/novedades', methods=['GET'])
def admin_listar_novedades():
    return listar_novedades_publico()


@app.route('/api/admin/novedades', methods=['POST'])
def admin_subir_novedad():
    try:
        datos = request.get_json() or {}
        titulo = texto_obligatorio(datos, 'titulo', 'título')
        contenido = texto_obligatorio(datos, 'contenido', 'contenido')
        ejecutar_cambio("INSERT INTO novedades (titulo, contenido) VALUES (%s, %s)", (titulo, contenido))
        return respuesta_ok(mensaje='Novedad publicada con éxito.', status_code=201)
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/admin/novedades/<int:id_novedad>', methods=['DELETE'])
def admin_eliminar_novedad(id_novedad):
    try:
        ejecutar_cambio("DELETE FROM novedades WHERE id = %s", (id_novedad,))
        return respuesta_ok(mensaje='Novedad eliminada correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/quejas', methods=['GET'])
def admin_listar_quejas():
    try:
        sql = """
            SELECT
                id_reporte AS id,
                nombre_completo,
                correo_contacto AS usuario_correo,
                detalle_queja AS descripcion,
                estado_reporte AS estado,
                fecha_registro
            FROM reportes_ayuda
            ORDER BY fecha_registro DESC
        """
        return respuesta_ok(ejecutar_select(sql), 'Quejas cargadas correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/admin/quejas/<int:id_queja>/estado', methods=['PUT'])
def admin_actualizar_estado_queja(id_queja):
    try:
        datos = request.get_json() or {}
        estado = texto_obligatorio(datos, 'estado', 'estado')
        ejecutar_cambio("UPDATE reportes_ayuda SET estado_reporte = %s WHERE id_reporte = %s", (estado, id_queja))
        return respuesta_ok(mensaje='Estado de la queja actualizado.')
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/admin/carreras-privadas', methods=['GET'])
def admin_listar_carreras():
    try:
        sql = """
            SELECT
                s.id_solicitud,
                s.nombre_cliente,
                s.telefono_cliente,
                s.direccion_origen,
                s.direccion_destino,
                s.monto_ofrecido,
                s.estado_solicitud,
                s.fecha_registro,
                s.fecha_aceptacion,
                s.chofer_id,
                CONCAT(c.nombres, ' ', c.apellidos) AS chofer_nombre,
                c.placa AS chofer_placa
            FROM solicitudes_carrera s
            LEFT JOIN choferes c ON c.id = s.chofer_id
            ORDER BY s.fecha_registro DESC
        """
        return respuesta_ok(ejecutar_select(sql), 'Carreras privadas cargadas correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


# ==========================================
# ENDPOINTS DEL CONDUCTOR
# ==========================================

@app.route('/api/conductor/<int:id_chofer>/perfil', methods=['GET'])
def conductor_perfil(id_chofer):
    try:
        sql = """
            SELECT id, nombres, apellidos, telefono, correo, placa, licencia, vehiculo, estado
            FROM choferes
            WHERE id = %s
            LIMIT 1
        """
        perfil = ejecutar_select(sql, (id_chofer,), uno=True)
        if not perfil:
            return respuesta_error('No se encontró el conductor.', 404)
        return respuesta_ok({k: normalizar_valor(v) for k, v in perfil.items()}, 'Perfil cargado correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/conductor/<int:id_chofer>/perfil', methods=['PUT'])
def conductor_actualizar_perfil(id_chofer):
    try:
        datos = request.get_json() or {}
        telefono = texto_obligatorio(datos, 'telefono', 'teléfono')
        correo = texto_obligatorio(datos, 'correo', 'correo').lower()
        password = str(datos.get('password', '')).strip()

        if password:
            sql = "UPDATE choferes SET telefono = %s, correo = %s, password = %s WHERE id = %s"
            params = (telefono, correo, password, id_chofer)
        else:
            sql = "UPDATE choferes SET telefono = %s, correo = %s WHERE id = %s"
            params = (telefono, correo, id_chofer)
        ejecutar_cambio(sql, params)
        return respuesta_ok(mensaje='Perfil actualizado correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


@app.route('/api/conductor/carreras', methods=['GET'])
def conductor_carreras_disponibles():
    try:
        sql = """
            SELECT id_solicitud, nombre_cliente, telefono_cliente, direccion_origen,
                   direccion_destino, monto_ofrecido, estado_solicitud, fecha_registro
            FROM solicitudes_carrera
            WHERE estado_solicitud = 'Pendiente'
            ORDER BY fecha_registro DESC
        """
        return respuesta_ok(ejecutar_select(sql), 'Carreras disponibles cargadas.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/conductor/<int:id_chofer>/mis-carreras', methods=['GET'])
def conductor_mis_carreras(id_chofer):
    try:
        sql = """
            SELECT id_solicitud, nombre_cliente, telefono_cliente, direccion_origen,
                   direccion_destino, monto_ofrecido, estado_solicitud, fecha_registro, fecha_aceptacion
            FROM solicitudes_carrera
            WHERE chofer_id = %s
            ORDER BY fecha_aceptacion DESC, fecha_registro DESC
        """
        return respuesta_ok(ejecutar_select(sql, (id_chofer,)), 'Tus carreras fueron cargadas.')
    except Error as e:
        return respuesta_error(str(e), 500)


@app.route('/api/conductor/carreras/<int:id_solicitud>/aceptar', methods=['PUT'])
def conductor_aceptar_carrera(id_solicitud):
    try:
        datos = request.get_json() or {}
        id_chofer = datos.get('chofer_id')
        if not id_chofer:
            raise ValueError('No se recibió el conductor.')

        sql = """
            UPDATE solicitudes_carrera
            SET estado_solicitud = 'Aceptada', chofer_id = %s, fecha_aceptacion = NOW()
            WHERE id_solicitud = %s AND estado_solicitud = 'Pendiente'
        """
        filas, _ = ejecutar_cambio(sql, (id_chofer, id_solicitud))
        if filas == 0:
            return respuesta_error('La carrera ya fue tomada o no está disponible.', 409)
        return respuesta_ok(mensaje='Carrera aceptada correctamente.')
    except Error as e:
        return respuesta_error(str(e), 500)
    except ValueError as e:
        return respuesta_error(str(e), 400)


if __name__ == '__main__':
    print('🚀 Servidor de Hijos de Cristo Rey levantado correctamente en http://127.0.0.1:5000')
    app.run(debug=True, port=5000)
