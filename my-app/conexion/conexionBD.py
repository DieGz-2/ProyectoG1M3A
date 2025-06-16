import mysql.connector

def connectionBD():
    print("INGRESO A LA CONEXION")
    try:
        connection = mysql.connector.connect(
            host="localhost",         # O usa "127.0.0.1"
            port=3308,                # ¡IMPORTANTE! Cambiado de 3306 a 3308
            user="root",
            passwd="admin",
            database="cloud",
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci',
            raise_on_warnings=True
        )
        if connection.is_connected():
            print("Conexión exitosa a la Base de Datos")
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")
