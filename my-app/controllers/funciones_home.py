# my-app/controllers/funciones_home.py

# Para subir archivo tipo foto al servidor (estas importaciones no se usan aquí)
# from werkzeug.utils import secure_filename
# import uuid 

from mysql.connector.errors import Error
from conexion.conexionBD import connectionBD 

import datetime
# import re # No usado en este archivo
import os

# from os import remove # No usado directamente para remover en estas funciones
# from os import path # os.path ya se usa con os.path.join

import openpyxl 
# biblioteca o modulo send_file para forzar la descarga (mover a router_home.py para send_file)
from flask import session # Mantener session porque accesosReporte la usa


# --- Funciones relacionadas con Accesos y Reportes ---
def accesosReporte():
    """
    Obtiene los registros de acceso a claves. Si el rol es 1 (admin),
    trae todos los accesos; de lo contrario, trae los accesos del usuario actual.
    """
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                if session.get('rol') == 1: # Si el rol es 1 (administrador)
                    querySQL = ("""
                        SELECT a.id_acceso, u.cedula, a.fecha, ar.nombre_area, a.clave
                        FROM accesos a
                        JOIN usuarios u ON u.id_usuario = a.id_usuario
                        JOIN area ar ON u.id_area = ar.id_area
                        ORDER BY u.cedula, a.fecha DESC
                    """)
                    cursor.execute(querySQL)
                else: # Para otros roles, mostrar solo sus propios accesos
                    cedula = session.get('cedula') 
                    if not cedula:
                        print("Error: Cédula no encontrada en la sesión para accesosReporte de usuario.")
                        return None
                    querySQL = ("""
                        SELECT a.id_acceso, u.cedula, a.fecha, ar.nombre_area, a.clave
                        FROM accesos a
                        JOIN usuarios u ON u.id_usuario = a.id_usuario
                        JOIN area ar ON u.id_area = ar.id_area
                        WHERE u.cedula = %s
                        ORDER BY u.cedula, a.fecha DESC
                    """)
                    cursor.execute(querySQL, (cedula,))
                
                accesosBD = cursor.fetchall()
                return accesosBD
    except Exception as e:
        print(f"Error en la función accesosReporte: {e}")
        return None

def generarReporteExcel():
    """
    Genera un archivo Excel con los datos de accesos y lo guarda.
    Retorna la ruta completa del archivo generado.
    """
    dataAccesos = accesosReporte() # Usa la función ya existente para obtener los datos
    if not dataAccesos:
        print("No hay datos de accesos para generar el reporte Excel.")
        return None 

    wb = openpyxl.Workbook()
    hoja = wb.active

    cabeceraExcel = ("ID", "CEDULA", "FECHA", "ÁREA", "CLAVE GENERADA")
    hoja.append(cabeceraExcel)

    for registro in dataAccesos:
        id_acceso = registro['id_acceso']
        cedula = registro['cedula']
        fecha = registro['fecha']
        area = registro['nombre_area']
        clave = registro['clave']
        hoja.append((id_acceso, cedula, fecha, area, clave))

    fecha_actual = datetime.datetime.now()
    cedula_sesion = session.get('cedula', 'anonimo') 
    archivoExcel = f"Reporte_accesos_{cedula_sesion}_{fecha_actual.strftime('%Y_%m_%d_%H%M%S')}.xlsx" # Añadido HHMMSS para unicidad
    
    # Ruta donde se guardará el excel
    carpeta_descarga = "static/downloads-excel" 
    ruta_descarga = os.path.join(os.getcwd(), carpeta_descarga) 

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # os.chmod(ruta_descarga, 0o755) # Generalmente no es necesario y puede causar problemas

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    return ruta_archivo # Ahora retorna la ruta del archivo

def dataReportes(): 
    """
    Obtiene todos los registros de acceso. Considera usar accesosReporte() directamente en las rutas
    para evitar redundancia, ya que accesosReporte maneja la lógica de rol.
    """
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT a.id_acceso, u.cedula, a.fecha, ar.nombre_area, a.clave
                FROM accesos a
                JOIN usuarios u ON u.id_usuario = a.id_usuario
                JOIN area ar ON u.id_area = ar.id_area
                ORDER BY u.cedula, a.fecha DESC
                """
                cursor.execute(querySQL)
                reportes = cursor.fetchall()
            return reportes
    except Exception as e:
        print(f"Error en dataReportes: {e}")
        return []

def lastAccessBD(cedula): 
    """
    Obtiene el último acceso registrado para una cédula específica.
    """
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT a.id_acceso, u.cedula, a.fecha, a.clave 
                FROM accesos a 
                JOIN usuarios u ON u.id_usuario = a.id_usuario 
                WHERE u.cedula = %s 
                ORDER BY a.fecha DESC 
                LIMIT 1
                """
                cursor.execute(querySQL, (cedula,))
                reporte = cursor.fetchone() 
            return reporte
    except Exception as e:
        print(f"Error en lastAccessBD: {e}")
        return None


# --- Funciones de Usuarios y Roles ---
def buscarAreaBD(search):
    """
    Busca áreas por nombre.
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT
                            a.id_area,
                            a.nombre_area
                        FROM area AS a
                        WHERE a.nombre_area LIKE %s
                        ORDER BY a.id_area DESC
                    """)
                search_pattern = f"%{search}%" 
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en buscarAreaBD: {e}")
        return []

def lista_usuariosBD():
    """
    Obtiene la lista de todos los usuarios.
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_usuario, cedula, nombre_usuario, apellido_usuario, id_area, id_rol FROM usuarios"
                cursor.execute(querySQL)
                usuariosBD = cursor.fetchall()
            return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD: {e}")
        return []

def lista_rolesBD():
    """
    Obtiene la lista de todos los roles disponibles.
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT * FROM rol"
                cursor.execute(querySQL)
                roles = cursor.fetchall()
            return roles
    except Exception as e:
        print(f"Error en lista_rolesBD: {e}")
        return []


# --- Funciones de Áreas ---
def lista_areasBD():
    """
    Obtiene la lista de todas las áreas.
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id_area, nombre_area FROM area"
                cursor.execute(querySQL)
                areasBD = cursor.fetchall()
            return areasBD
    except Exception as e:
        print(f"Error en lista_areasBD: {e}")
        return []

def guardarArea(area_name):
    """
    Guarda una nueva área en la base de datos.
    Retorna el número de filas afectadas (1 si éxito, 0 si no, o False si error).
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = "INSERT INTO area (nombre_area) VALUES (%s)"
                valores = (area_name,)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_insert = mycursor.rowcount
                return resultado_insert
    except Exception as e:
        print(f'Se produjo un error en guardarArea: {str(e)}')
        return 0 


def actualizarArea(area_id, area_name):
    """
    Actualiza el nombre de un área existente.
    Retorna el número de filas afectadas (1 si éxito, 0 si no, o False si error).
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                sql = """UPDATE area SET nombre_area = %s WHERE id_area = %s"""
                valores = (area_name, area_id)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                resultado_update = mycursor.rowcount
                return resultado_update
    except Exception as e:
        print(f'Se produjo un error al actualizar el área: {str(e)}')
        return 0 


def eliminarArea(id_area): 
    """
    Elimina un área de la base de datos por su ID.
    Retorna el número de filas afectadas (1 si éxito, 0 si no, o False si error).
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor: 
                querySQL = "DELETE FROM area WHERE id_area=%s"
                cursor.execute(querySQL, (id_area,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount
        return resultado_eliminar 
    except Error as e: 
        print(f"Error MySQL al eliminarArea: {e}")
        return False 
    except Exception as e:
        print(f"Error inesperado en eliminarArea: {e}")
        return False


# --- Funciones de Equipos ---
def lista_equiposBD():
    """
    Obtiene la lista de todos los equipos del inventario.
    """
    equipos = []
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = """
                SELECT
                    id_equipo,
                    numero_serie,
                    marca,
                    modelo,
                    tipo_dispositivo,
                    procesador,
                    ram_capacidad,
                    almacenamiento,
                    sistema_operativo,
                    estado,
                    ubicacion,
                    fecha_adquisicion,
                    usuario_asignado
                FROM equipos
                ORDER BY id_equipo DESC;
                """
                cursor.execute(querySQL)
                equipos = cursor.fetchall()
        return equipos
    except Exception as e:
        print(f"Error en lista_equiposBD: {e}")
        return []

def guardarEquipo(numero_serie, marca, modelo, tipo_dispositivo, procesador, ram_capacidad,
                  almacenamiento, sistema_operativo, estado, ubicacion, fecha_adquisicion, usuario_asignado):
    """
    Guarda un nuevo equipo en la base de datos.
    Retorna el número de filas afectadas (1 si éxito, False si error).
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as mycursor:
                sql = """
                INSERT INTO equipos (numero_serie, marca, modelo, tipo_dispositivo, procesador,
                                     ram_capacidad, almacenamiento, sistema_operativo, estado,
                                     ubicacion, fecha_adquisicion, usuario_asignado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (numero_serie, marca, modelo, tipo_dispositivo, procesador,
                           ram_capacidad, almacenamiento, sistema_operativo, estado,
                           ubicacion, fecha_adquisicion, usuario_asignado)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                return mycursor.rowcount 
    except Error as e:
        print(f"Error MySQL al guardarEquipo: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado en guardarEquipo: {e}")
        return False

def actualizarEquipoBD(id_equipo, numero_serie, marca, modelo, tipo_dispositivo, procesador,
                       ram_capacidad, almacenamiento, sistema_operativo, estado,
                       ubicacion, fecha_adquisicion, usuario_asignado):
    """
    Actualiza un equipo existente en la base de datos.
    Retorna el número de filas afectadas (1 si éxito, False si error).
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as mycursor:
                sql = """
                UPDATE equipos SET
                    numero_serie = %s,
                    marca = %s,
                    modelo = %s,
                    tipo_dispositivo = %s,
                    procesador = %s,
                    ram_capacidad = %s,
                    almacenamiento = %s,
                    sistema_operativo = %s,
                    estado = %s,
                    ubicacion = %s,
                    fecha_adquisicion = %s,
                    usuario_asignado = %s
                WHERE id_equipo = %s
                """
                valores = (numero_serie, marca, modelo, tipo_dispositivo, procesador,
                           ram_capacidad, almacenamiento, sistema_operativo, estado,
                           ubicacion, fecha_adquisicion, usuario_asignado, id_equipo)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                return mycursor.rowcount 
    except Error as e:
        print(f"Error MySQL al actualizarEquipoBD: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado en actualizarEquipoBD: {e}")
        return False

def eliminarEquipoBD(id_equipo):
    """
    Elimina un equipo de la base de datos por su ID.
    Retorna True si la eliminación fue exitosa, False si hubo un error.
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as cursor:
                querySQL = "DELETE FROM equipos WHERE id_equipo = %s"
                cursor.execute(querySQL, (id_equipo,))
                conexion_MySQLdb.commit()
                return True 
    except Error as e:
        print(f"Error MySQL al eliminarEquipoBD: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado en eliminarEquipoBD: {e}")
        return False


# --- Funciones de Generación de Claves ---
import random
import string

def crearClave():
    """
    Genera una clave alfanumérica aleatoria de 6 caracteres.
    """
    caracteres = string.ascii_letters + string.digits 
    longitud = 6 
    clave = ''.join(random.choice(caracteres) for _ in range(longitud))
    print("La clave generada es:", clave) # Para depuración
    return clave

def guardarClaveAuditoria(clave_audi, id_usuario):
    """
    Guarda una clave generada y la asocia a un usuario en la tabla de accesos.
    Retorna el número de filas afectadas (1 si éxito, 0 si no, o False si error).
    """
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor() as mycursor: 
                sql = "INSERT INTO accesos (fecha, clave, id_usuario) VALUES (NOW(),%s,%s)"
                valores = (clave_audi, id_usuario)
                mycursor.execute(sql, valores)
                conexion_MySQLdb.commit()
                return mycursor.rowcount 
    except Exception as e:
        print(f'Se produjo un error en guardarClaveAuditoria: {str(e)}')
        return 0 


# --- Funciones de Gráficos ---
def obtenerroles():
    """
    Obtiene la lista de nombres de roles para gráficos.
    """
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                query = """
                    SELECT r.nombre_rol
                    FROM rol r
                    ORDER BY r.nombre_rol ASC
                """
                cursor.execute(query)
                roles = cursor.fetchall()
            return roles
    except Exception as e:
        print(f"Error en obtenerroles: {e}")
        return []

def obtener_areas():
    """
    Obtiene el nombre y número de personas de las áreas para gráficos.
    """
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                query = """
                    SELECT nombre_area, numero_personas
                    FROM area
                    ORDER BY nombre_area ASC
                """
                cursor.execute(query)
                areas = cursor.fetchall()
            return areas
    except Exception as e:
        print(f"Error en obtener_areas: {e}")
        return []

def obtener_accesos_por_fecha(fecha_inicio, fecha_fin):
    """
    Obtiene la cantidad de accesos por clave en un rango de fechas.
    """
    try:
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                query = """
                    SELECT clave, COUNT(id_acceso) AS cantidad
                    FROM accesos
                    WHERE fecha BETWEEN %s AND %s
                    GROUP BY clave
                    ORDER BY clave ASC
                """
                cursor.execute(query, (fecha_inicio, fecha_fin))
                accesos = cursor.fetchall()
            return accesos
    except Exception as e:
        print(f"Error en obtener_accesos_por_fecha: {e}")
        return []