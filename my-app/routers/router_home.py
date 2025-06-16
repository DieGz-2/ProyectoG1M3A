# router_home.py

from controllers.funciones_login import *
from app import app
from flask import render_template, request, flash, redirect, url_for, session, jsonify
from mysql.connector.errors import Error

# Importando todas las funciones de BD de funciones_home
# Asegúrate de que este archivo contiene:
# lista_areasBD, lista_equiposBD, lista_usuariosBD, eliminarUsuario, eliminarArea,
# dataReportes, lastAccessBD, crearClave, guardarClaveAuditoria, lista_rolesBD,
# guardarArea, actualizarArea, guardarEquipo, actualizarEquipoBD, eliminarEquipoBD
from controllers.funciones_home import *


@app.route('/lista-de-areas', methods=['GET'])
def lista_areas():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_areas.html', areas=lista_areasBD(), dataLogin=dataLoginSesion())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

# RUTA PARA LISTAR EQUIPOS
@app.route('/lista-de-lab', methods=['GET'])
def lista_labs():
    if 'conectado' in session:
        try:
            equipos_data = lista_equiposBD() # Llama a tu función para obtener los equipos
        except Exception as e:
            print(f"Error al cargar equipos: {e}")
            equipos_data = [] # En caso de error, muestra una lista vacía
            flash('Error al cargar la lista de equipos.', 'error')

        return render_template('public/usuarios/lista_lab.html', equipos=equipos_data, dataLogin=dataLoginSesion())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=lista_usuariosBD(), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles = lista_rolesBD())
    else:
        flash('Primero debes iniciar sesión.', 'error') # Agregado flash message
        return redirect(url_for('inicio')) # Redirige al inicio, no a inicioCpanel


# RUTA ESPECIFICADA PARA ELIMINAR UN USUARIO
@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
    else:
        flash('Hubo un error al eliminar el usuario.', 'error') # Mensaje más genérico de error
    return redirect(url_for('usuarios'))


# RUTA ESPECIFICADA PARA ELIMINAR UN AREA
@app.route('/borrar-area/<string:id_area>/', methods=['GET'])
def borrarArea(id_area):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    resp = eliminarArea(id_area) # Asumo que eliminaArea retorna True/False o un rowcount
    if resp:
        flash('El Área fue eliminada correctamente', 'success') # <-- Corregido el mensaje aquí
    else:
        # Esto podría significar que no se encontró el área o que hay elementos relacionados (ej. usuarios)
        flash('Hubo un error al eliminar el área, o hay elementos asociados a ella.', 'error')
    return redirect(url_for('lista_areas'))


@app.route("/descargar-informe-accesos/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReporteExcel()
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    
@app.route("/reporte-accesos", methods=['GET'])
def reporteAccesos():
    if 'conectado' in session:
        userData = dataLoginSesion()
        # Asegúrate que 'cedula' existe en userData antes de pasarlo a lastAccessBD
        cedula_usuario = userData.get('cedula') if userData else None
        
        # Si cedula_usuario es None, lastAccessBD debería manejarlo o podrías pasar None explícitamente
        last_access_data = lastAccessBD(cedula_usuario) if cedula_usuario else None

        return render_template('public/perfil/reportes.html', 
                               reportes=dataReportes(),
                               lastAccess=last_access_data, # Pasa el resultado de la función
                               dataLogin=dataLoginSesion())
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/interfaz-clave", methods=['GET','POST'])
def claves():
    # Esta ruta parece ser solo para mostrar el formulario de generación de clave
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
    return render_template('public/usuarios/generar_clave.html', dataLogin=dataLoginSesion())
    
# RUTA PARA GENERAR Y GUARDAR CLAVE
@app.route('/generar-y-guardar-clave/<string:id_usuario>', methods=['GET','POST'])
def generar_clave(id_usuario): # Cambiado 'id' a 'id_usuario' para claridad
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    try:
        clave_generada = crearClave()
        # Asumo que guardarClaveAuditoria retorna el número de filas afectadas (1 si éxito)
        resultado_guardado = guardarClaveAuditoria(clave_generada, id_usuario) 

        if resultado_guardado:
            flash(f'Clave generada y guardada correctamente: {clave_generada}', 'success')
        else:
            flash('Error al guardar la clave generada.', 'error')
    except Exception as e:
        flash(f'Ocurrió un error al generar o guardar la clave: {e}', 'error')
        print(f"Error en generar_clave: {e}")

    # Redirige a una página donde se pueda ver el resultado, por ejemplo, los reportes o la lista de usuarios.
    # Podrías querer redirigir a donde el usuario vea la clave o un mensaje.
    return redirect(url_for('reporteAccesos')) # O a 'usuarios' si el ID es de un usuario


# RUTA PARA CREAR AREA
@app.route('/crear-area', methods=['GET','POST'])
def crearArea():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        try:
            area_name = request.form['nombre_area']
            resultado_insert = guardarArea(area_name)
            if resultado_insert:
                flash('El Área fue creada correctamente', 'success')
            else:
                flash('Hubo un error al guardar el área.', 'error') # Mensaje de error más descriptivo
        except Exception as e:
            flash(f'Ocurrió un error inesperado al crear el área: {e}', 'error')
            print(f"Error al crearArea: {e}")
        return redirect(url_for('lista_areas'))
    # Si es GET, simplemente redirige o muestra un formulario si lo tuvieras separado
    return redirect(url_for('lista_areas')) # Redirige si se accede con GET


# RUTA PARA ACTUALIZAR AREA
@app.route('/actualizar-area', methods=['POST'])
def updateArea():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        try:
            nombre_area = request.form['nombre_area']
            id_area = request.form['id_area']
            resultado_update = actualizarArea(id_area, nombre_area)
            if resultado_update:
                flash('El área fue actualizada correctamente', 'success')
            else:
                flash('Hubo un error al actualizar el área. Verifique los datos.', 'error')
        except Exception as e:
            flash(f'Ocurrió un error inesperado al actualizar el área: {e}', 'error')
            print(f"Error al updateArea: {e}")
        return redirect(url_for('lista_areas'))
    return redirect(url_for('lista_areas'))


# RUTA PARA CREAR EQUIPO
@app.route('/crear-equipo', methods=['POST'])
def crearEquipo():
    if 'conectado' not in session: # Siempre verificar sesión
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        try:
            numero_serie = request.form.get('numero_serie')
            marca = request.form.get('marca')
            modelo = request.form.get('modelo')
            tipo_dispositivo = request.form.get('tipo_dispositivo')
            procesador = request.form.get('procesador')
            ram_capacidad = request.form.get('ram_capacidad')
            almacenamiento = request.form.get('almacenamiento')
            sistema_operativo = request.form.get('sistema_operativo')
            estado = request.form.get('estado')
            ubicacion = request.form.get('ubicacion')
            fecha_adquisicion = request.form.get('fecha_adquisicion')
            usuario_asignado = request.form.get('usuario_asignado') # Puede ser None si el campo no se envía

            if not all([numero_serie, marca, modelo, tipo_dispositivo, estado, ubicacion, fecha_adquisicion]):
                flash('Todos los campos obligatorios deben ser completados.', 'error')
                return redirect(url_for('lista_labs'))

            resultado_guardado = guardarEquipo(
                numero_serie, marca, modelo, tipo_dispositivo, procesador,
                ram_capacidad, almacenamiento, sistema_operativo, estado,
                ubicacion, fecha_adquisicion, usuario_asignado
            )

            if resultado_guardado:
                flash('Equipo creado correctamente!', 'success')
            else:
                flash('Hubo un error al crear el equipo. Puede que el número de serie ya exista o faltan datos.', 'error')

        except Exception as e:
            flash(f'Ocurrió un error inesperado al procesar la creación: {e}', 'error')
            print(f"Error al crear equipo: {e}")

        return redirect(url_for('lista_labs'))
    
    return redirect(url_for('lista_labs'))


# RUTA PARA ACTUALIZAR EQUIPO
@app.route('/actualizar-equipo', methods=['POST'])
def updateEquipo():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    if request.method == 'POST':
        try:
            id_equipo = request.form.get('id_equipo')
            numero_serie = request.form.get('numero_serie')
            marca = request.form.get('marca')
            modelo = request.form.get('modelo')
            tipo_dispositivo = request.form.get('tipo_dispositivo')
            procesador = request.form.get('procesador')
            ram_capacidad = request.form.get('ram_capacidad')
            almacenamiento = request.form.get('almacenamiento')
            sistema_operativo = request.form.get('sistema_operativo')
            estado = request.form.get('estado')
            ubicacion = request.form.get('ubicacion')
            fecha_adquisicion = request.form.get('fecha_adquisicion')
            usuario_asignado = request.form.get('usuario_asignado')

            if not all([id_equipo, numero_serie, marca, modelo, tipo_dispositivo, estado, ubicacion, fecha_adquisicion]):
                flash('Todos los campos obligatorios deben ser completados para actualizar.', 'error')
                return redirect(url_for('lista_labs'))

            resultado_update = actualizarEquipoBD(
                id_equipo, numero_serie, marca, modelo, tipo_dispositivo,
                procesador, ram_capacidad, almacenamiento, sistema_operativo,
                estado, ubicacion, fecha_adquisicion, usuario_asignado
            )

            if resultado_update:
                flash('Equipo actualizado exitosamente!', 'success')
            else:
                flash('Hubo un error al actualizar el equipo. Verifique los datos.', 'error')

        except Exception as e:
            flash(f'Ocurrió un error inesperado al procesar la actualización: {e}', 'error')
            print(f"Error al actualizar equipo: {e}")

        return redirect(url_for('lista_labs'))
    
    return redirect(url_for('lista_labs'))


# RUTA PARA ELIMINAR EQUIPO
@app.route('/borrar-equipo/<string:id_equipo>/', methods=['GET'])
def borrarEquipo(id_equipo):
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))

    try:
        resp = eliminarEquipoBD(id_equipo) # Asumo que esta función retorna True/False
        if resp:
            flash('El Equipo fue eliminado correctamente', 'success')
        else:
            flash('Hubo un error al eliminar el equipo o no se encontró.', 'error')
    except Exception as e:
        flash(f'Ocurrió un error inesperado al intentar eliminar el equipo: {e}', 'error')
        print(f"Error al eliminar equipo: {e}")

    return redirect(url_for('lista_labs')) # Siempre redirige a la lista