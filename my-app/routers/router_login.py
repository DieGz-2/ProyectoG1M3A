
from app import app
from flask import render_template, request, flash, redirect, url_for, session
from flask import jsonify
from controllers.funciones_home import obtenerroles

# Importando mi conexión a BD
from conexion.conexionBD import connectionBD

# Para encriptar contraseña generate_password_hash
from werkzeug.security import check_password_hash

# Importando controllers para el modulo de login
from controllers.funciones_login import *
from controllers.funciones_home import *
PATH_URL_LOGIN = "/public/login"


@app.route('/', methods=['GET'])
def inicio():
    if 'conectado' in session:
        return render_template('public/base_cpanel.html', dataLogin=dataLoginSesion())
    else:
        return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/mi-perfil/<string:id>', methods=['GET'])
def perfil(id):
    if 'conectado' in session:
        
        return render_template(f'public/perfil/perfil.html', info_perfil_session=info_perfil_session(id), dataLogin=dataLoginSesion(), areas=lista_areasBD(), roles=lista_rolesBD())
    else:
        return redirect(url_for('inicio'))


# Crear cuenta de usuario
@app.route('/register-user', methods=['GET'])
def cpanelRegisterUser():
        return render_template(f'{PATH_URL_LOGIN}/auth_register.html',dataLogin = dataLoginSesion(),areas=lista_areasBD(), roles=lista_rolesBD())


# Recuperar cuenta de usuario
@app.route('/recovery-password', methods=['GET'])
def cpanelRecoveryPassUser():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        return render_template(f'{PATH_URL_LOGIN}/auth_forgot_password.html')


# Crear cuenta de usuario
@app.route('/saved-register', methods=['POST'])
def cpanelRegisterUserBD():
    if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:
        cedula = request.form['cedula']
        name = request.form['name']
        surname = request.form['surname']
        id_area = request.form['selectArea']
        id_rol = request.form['selectRol']
        pass_user = request.form['pass_user']

        resultData = recibeInsertRegisterUser(
            cedula, name, surname, id_area,id_rol,pass_user)
        if (resultData != 0):
            flash('la cuenta fue creada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            return redirect(url_for('inicio'))
    else:
        flash('el método HTTP es incorrecto', 'error')
        return redirect(url_for('inicio'))


# Actualizar datos de mi perfil
@app.route("/actualizar-datos-perfil/<int:id>", methods=['POST'])
def actualizarPerfil(id):
    if request.method == 'POST':
        if 'conectado' in session:
            respuesta = procesar_update_perfil(request.form,id)
            if respuesta == 1:
                flash('Los datos fuerón actualizados correctamente.', 'success')
                return redirect(url_for('inicio'))
            elif respuesta == 0:
                flash(
                    'La contraseña actual esta incorrecta, por favor verifique.', 'error')
                return redirect(url_for('perfil',id=id))
            elif respuesta == 2:
                flash('Ambas claves deben se igual, por favor verifique.', 'error')
                return redirect(url_for('perfil',id=id))
            elif respuesta == 3:
                flash('La Clave actual es obligatoria.', 'error')
                return redirect(url_for('perfil',id=id))
            else: 
                flash('Clave actual incorrecta', 'error')
                return redirect(url_for('perfil',id=id))
        else:
            flash('primero debes iniciar sesión.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Validar sesión
@app.route('/login', methods=['GET', 'POST'])
def loginCliente():
    if 'conectado' in session:
        return redirect(url_for('inicio'))
    else:
        if request.method == 'POST' and 'cedula' in request.form and 'pass_user' in request.form:

            cedula = str(request.form['cedula'])
            pass_user = str(request.form['pass_user'])
            conexion_MySQLdb = connectionBD()
            print(conexion_MySQLdb)
            cursor = conexion_MySQLdb.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM usuarios WHERE cedula = %s", [cedula])
            account = cursor.fetchone()

            if account:
                if check_password_hash(account['password'], pass_user):
                    # Crear datos de sesión, para poder acceder a estos datos en otras rutas
                    session['conectado'] = True
                    session['id'] = account['id_usuario']
                    session['name'] = account['nombre_usuario']
                    session['cedula'] = account['cedula']
                    session['rol'] = account['id_rol']

                    flash('la sesión fue correcta.', 'success')
                    return redirect(url_for('inicio'))
                else:
                    # La cuenta no existe o el nombre de usuario/contraseña es incorrecto
                    flash('datos incorrectos por favor revise.', 'error')
                    return render_template(f'{PATH_URL_LOGIN}/base_login.html')
            else:
                flash('el usuario no existe, por favor verifique.', 'error')
                return render_template(f'{PATH_URL_LOGIN}/base_login.html')
        else:
            flash('primero debes iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')


@app.route('/closed-session',  methods=['GET'])
def cerraSesion():
    if request.method == 'GET':
        if 'conectado' in session:
            # Eliminar datos de sesión, esto cerrará la sesión del usuario
            session.pop('conectado', None)
            session.pop('id', None)
            session.pop('name_surname', None)
            session.pop('email', None)
            flash('tu sesión fue cerrada correctamente.', 'success')
            return redirect(url_for('inicio'))
        else:
            flash('recuerde debe iniciar sesión.', 'error')
            return render_template(f'{PATH_URL_LOGIN}/base_login.html')
#--------------------- metodo de graficas ----------------------

@app.route('/lista-de-graficas')
def lista_de_graficas():
    if 'conectado' in session:
        # Simulación de datos de sesión para dataLogin
        dataLogin = {
            "id": session.get("id"),
            "rol": session.get("rol"),  # Asegúrate de que 'rol' esté en la sesión
        }
        return render_template('public/grafica/lista_graficas.html', dataLogin=dataLogin)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('loginCliente'))
    #-----------------------------------------------------------
@app.route('/grafica_roles_datos', methods=['GET'])
def grafica_roles_datos():
    try:
        roles = obtenerroles()  # Llama a la función que obtiene los datos de roles
        nombres = [rol['nombre_rol'] for rol in roles]
        return jsonify({"nombres": nombres})  # Devuelve solo los nombres de los roles
    except Exception as e:
        print(f"Error en grafica_roles_datos: {e}")
        return jsonify({"error": "Error al obtener los datos"}), 500
    
    #--------------------- areas -----------------------------------
@app.route('/grafica_areas_datos', methods=['GET'])
def grafica_areas_datos():
    try:
        areas = obtener_areas()  # Llama a la función que obtiene los datos de las áreas
        nombres = [area['nombre_area'] for area in areas]
        cantidades = [area['numero_personas'] for area in areas]
        return jsonify({"nombres": nombres, "cantidades": cantidades})  # Devuelve los datos en formato JSON
    except Exception as e:
        print(f"Error en grafica_areas_datos: {e}")
        return jsonify({"error": "Error al obtener los datos"}), 500
    #-------------------------------- accesos a datos--------------------
@app.route('/grafica_accesos_datos', methods=['GET'])
def grafica_accesos_datos():
    try:
        # Obtener las fechas de los parámetros de la URL
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')

        if not fecha_inicio or not fecha_fin:
            return jsonify({"error": "Debe proporcionar las fechas de inicio y fin"}), 400

        accesos = obtener_accesos_por_fecha(fecha_inicio, fecha_fin)
        claves = [acceso['clave'] for acceso in accesos]
        cantidades = [acceso['cantidad'] for acceso in accesos]

        return jsonify({"claves": claves, "cantidades": cantidades})
    except Exception as e:
        print(f"Error en grafica_accesos_datos: {e}")
        return jsonify({"error": "Error al obtener los datos"}), 500
    #------------------------ acesso de datos por usuario---------------------
@app.route('/obtener_nombres_usuarios', methods=['GET'])
def obtener_nombres_usuarios():
    try:
        # Consultar los nombres de los usuarios
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                query = "SELECT nombre_usuario FROM usuarios ORDER BY nombre_usuario ASC"
                cursor.execute(query)
                usuarios = cursor.fetchall()

        # Preparar los datos para el frontend
        nombres = [usuario['nombre_usuario'] for usuario in usuarios]

        return jsonify({"nombres": nombres})
    except Exception as e:
        print(f"Error en obtener_nombres_usuarios: {e}")
        return jsonify({"error": "Error al obtener los nombres de los usuarios"}), 500
    
@app.route('/grafica_fechas_usuario_datos', methods=['GET'])


#---------------------------------------------------------------------
def grafica_fechas_usuario_datos():
    try:
        # Obtener el nombre del usuario de los parámetros de la URL
        nombre_usuario = request.args.get('nombre_usuario')

        if not nombre_usuario:
            return jsonify({"error": "Debe proporcionar el nombre del usuario"}), 400

        # Consultar las fechas de acceso del usuario
        with connectionBD() as conexion_MYSQLdb:
            with conexion_MYSQLdb.cursor(dictionary=True) as cursor:
                query = """
                    SELECT a.fecha
                    FROM accesos a
                    INNER JOIN usuarios u ON a.id_usuario = u.id_usuario
                    WHERE u.nombre_usuario = %s
                    ORDER BY a.fecha ASC
                """
                cursor.execute(query, (nombre_usuario,))
                accesos = cursor.fetchall()

        # Preparar los datos para la gráfica
        fechas = [acceso['fecha'] for acceso in accesos]

        return jsonify({"fechas": fechas})
    except Exception as e:
        print(f"Error en grafica_fechas_usuario_datos: {e}")
        return jsonify({"error": "Error al obtener los datos"}), 500