import mysql.connector

# Aquí centralizamos las credenciales de tu MySQL Workbench
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'admin',
    'port': 3309,
    'database': 'bd_cristorey'
}

# Función única para exportar la conexión
def get_db_connection():
    return mysql.connector.connect(**db_config)