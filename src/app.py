from venv import logger
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask import flash
import pymysql
import random
from flask_mysqldb import MySQL, MySQLdb
from dao.DAOUsuario import DAOUsuario
from dao.DAOCliente import DAOCliente
from dao.DAOCategoria import DAOCategoria
from dao.DAOProducto import DAOProducto
from dao.DAOPedido import DAOPedido
from dao.DAOMensaje import DAOMensaje

app = Flask(__name__)
app.secret_key = "mys3cr3tk3y"
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_poo'

mysql = MySQL(app)
db_usuario = DAOUsuario()
db_cliente = DAOCliente()
db_categoria = DAOCategoria()
db_producto = DAOProducto()
db_pedido = DAOPedido()
db_mensaje = DAOMensaje()

@app.route("/inicio_sesion")

def inicio_sesion():
    if 'logueado2' in session and session['logueado2']:
        return render_template("index_tienda.html")
    else:
        return render_template("inicio_sesion.html")

@app.route('/acceso-login', methods=["GET", "POST"])
def login():
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']

        # Intenta encontrar el usuario en la tabla de usuarios
        cur_usuario = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur_usuario.execute('SELECT * FROM usuario WHERE email = %s AND password = %s', (_correo, _password))
        account = cur_usuario.fetchone()

        # Intenta encontrar el cliente en la tabla de clientes
        cur_cliente = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur_cliente.execute('SELECT * FROM cliente WHERE email = %s AND password = %s', (_correo, _password))
        account_cliente = cur_cliente.fetchone()

        if account:
            if account['estado'] == 'Activo':
                # Almacena las variables del usuario en la sesión
                session['logueado'] = True
                session['id'] = account['id']
                session['nombre_usuario'] = account['nombre']
                session['apellidos_usuario'] = account['apellido']
                session['imagen_usuario'] = account['imagen']
                session['direccion_usuario'] = account['direccion']
                session['telefono_usuario'] = account['telefono']
                session['cargo_usuario'] = account['rol']
                session['dni_usuario'] = account['dni']
                session['carrera_usuario'] = account['carrera']
                session['fecha_usuario'] = account['fecha']
                session['estado_usuario'] = account['estado']
                session['dato_facebook_url'] = account['facebook_url']
                session['dato_instagram_url'] = account['instagram_url']
                session['dato_linkedin_url'] = account['linkedin_url']

                return redirect(url_for('index'))

            else:
                return render_template("inicio_sesion.html", mensaje="Usuario inactivo. Contacta al administrador para obtener ayuda.")
        elif account_cliente:
            # Almacena las variables del cliente en la sesión
            session['logueado2'] = True
            session['id'] = account_cliente['id']
            session['nombre_cliente'] = account_cliente['nombre']
            session['apellido_cliente'] = account_cliente['apellido']
            if 'foto_perfil' in account_cliente and account_cliente['foto_perfil']:
                session['foto_cliente'] = account_cliente['foto_perfil']
            else:
                session['foto_cliente'] = 'foto_cliente.png'
            session['dni_cliente'] = account_cliente['dni']
            session['telefono_cliente'] = account_cliente['telefono']
            session['correo_cliente'] = account_cliente['email']
            # ... (agrega otras variables según sea necesario)
            return redirect(url_for('index_principal'))
        else:
            return render_template("inicio_sesion.html", mensaje="Usuario y/o contraseña incorrecto(s)")
    else:
        return render_template("inicio_sesion.html", mensaje="Faltan datos en el formulario de inicio de sesión")
    

    
@app.route("/registrarse")

def registrarse():
    return render_template("registrarse.html")

@app.route("/registro",methods=['POST'])
def registro():
    nombre = request.form['nombre']
    password = request.form['password']
    email = request.form['email']
    telefono = request.form['telefono']
    apellido = request.form['apellido']
    dni = request.form['dni']
    cur = mysql.connection.cursor()
    cur.execute('insert into cliente(nombre,apellido,telefono,dni,email,password) values(%s,%s,%s,%s,%s,%s)', (nombre,apellido,telefono,dni,email,password))
    mysql.connection.commit()
    return render_template("inicio_sesion.html",mensaje="Cuenta creada con exito")

@app.route("/recuperar",methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        correo = request.form.get('email')

        # Verificar si el correo existe en la base de datos
        if verificar_correo_existente(correo):
            # Redirigir al usuario a la página para cambiar la contraseña
            return redirect(url_for('cambiar_contrasena', correo=correo))
        else:
            flash('Correo electrónico no encontrado. Verifica la dirección e inténtalo nuevamente.', 'error')

    return render_template('recuperar.html')

def verificar_correo_existente(correo):
    # Conectar a la base de datos
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    cursor = connection.cursor()

    # Consultar si el correo existe en la base de datos
    query = "SELECT COUNT(*) FROM cliente WHERE email = %s"
    cursor.execute(query, (correo,))
    resultado = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return resultado > 0

@app.route('/cambiar_contrasena/<correo>', methods=['GET', 'POST'])
def cambiar_contrasena(correo):
    if request.method == 'POST':
        nueva_contrasena = request.form.get('nueva_contrasena')
        confirmar_contrasena = request.form.get('confirmar_contrasena')
        # Verificar si las contraseñas coinciden
        if nueva_contrasena == confirmar_contrasena:

            # Actualizar la contraseña en la base de datos para el correo dado
            if actualizar_contrasena(correo, nueva_contrasena):
                flash('Contraseña cambiada exitosamente. Ahora puedes iniciar sesión con la nueva contraseña.', 'success')
                return redirect(url_for('recuperar'))
            else:
                flash('Hubo un problema al cambiar la contraseña. Inténtalo nuevamente más tarde.', 'error')
        else:
            flash('Las contraseñas no coinciden. Por favor, inténtalo nuevamente.', 'error')

    return render_template('cambiar_contrasena.html', correo=correo)

def actualizar_contrasena(correo, nueva_contrasena_hash):
    # Conectar a la base de datos
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    cursor = connection.cursor()

    try:
        # Actualizar la contraseña en la base de datos
        query = "UPDATE cliente SET password = %s WHERE email = %s"
        cursor.execute(query, (nueva_contrasena_hash, correo))
        connection.commit()
        return True
    except Exception as e:
        print(f"Error al actualizar la contraseña: {str(e)}")
        connection.rollback()
        return False
    finally:
        cursor.close()
        connection.close()



@app.route("/index")

def index():
    datos = db_mensaje.read(None)
    return render_template("index.html", nombre_usuario=session['nombre_usuario'], imagen_usuario=session['imagen_usuario'], apellidos_usuario=session['apellidos_usuario'], direccion_usuario=session['direccion_usuario'],telefono_usuario=session['telefono_usuario'],cargo_usuario=session['cargo_usuario'], dni_usuario=session['dni_usuario'], carrera_usuario=session['carrera_usuario'], fecha_usuario=session['fecha_usuario'],estado_usuario=session['estado_usuario'], dato_facebook_url=session['dato_facebook_url'], dato_instagram_url=session['dato_instagram_url'], dato_linkedin_url=session['dato_linkedin_url'], data=datos)


@app.route("/perfil")

def perfil():
    usuario_id = session.get('id')
    datos = db_usuario.read(usuario_id)
    return render_template("perfil.html", data=datos)

#----------------------------------------------------------------USUARIO----------------------------------------------------------------

@app.route('/usuario/')

def usuario():
    datos = db_usuario.read(None)
    return render_template('usuario/index.html', data=datos)

@app.route('/usuario/add/')

def add():
    return render_template('usuario/add.html')

@app.route('/usuario/addusuario/', methods=['POST', 'GET'])
def addusuario():
    if request.method == 'POST' and request.form['save']:
        rol = request.form['rol']
        estado = request.form['estado']

        if rol == 'Escoger...' or estado == 'Escoger...':
            flash("Por favor, selecciona opciones válidas para Rol y Estado.")
        else:
            if db_usuario.insert(request.form):
                flash("Nuevo usuario creado")
            else:
                flash("ERROR al crear usuario")

    return redirect(url_for('usuario'))    

@app.route('/usuario/update/<int:id>/')
def update(id):
    data = db_usuario.read(id)

    if len(data) == 0:
        return redirect(url_for('usuario'))
    else:
        session['update'] = id
        return render_template('usuario/update.html', data=data)

@app.route('/usuario/updateusuario', methods=['POST'])
def updateusuario():
    if request.method == 'POST' and 'update' in request.form:
        user_id_to_update = session['update']
        if db_usuario.update(user_id_to_update, request.form):
            flash('Se actualizó correctamente')

            # Verifica si el usuario actualizado es el mismo que el usuario en sesión
            if user_id_to_update == session['id']:
                # Actualiza la sesión solo si es el mismo usuario
                usuario_actualizado = db_usuario.read(user_id_to_update)[0]
                session['nombre_usuario'] = usuario_actualizado[1]
                session['apellidos_usuario'] = usuario_actualizado[2]
                session['imagen_usuario'] = usuario_actualizado[7]
                session['direccion_usuario'] = usuario_actualizado[9]
                session['telefono_usuario'] = usuario_actualizado[5]
                session['cargo_usuario'] = usuario_actualizado[6]
                session['dni_usuario'] = usuario_actualizado[10]
                session['carrera_usuario'] = usuario_actualizado[11]
                session['fecha_usuario'] = usuario_actualizado[12]
                session['estado_usuario'] = usuario_actualizado[8]
                session['dato_facebook_url'] = usuario_actualizado[13]
                session['dato_instagram_url'] = usuario_actualizado[14]
                session['dato_linkedin_url'] = usuario_actualizado[15]
                # Actualiza otros campos según sea necesario

            session.pop('update', None)
        else:
            flash('ERROR al actualizar')

        return redirect(url_for('usuario'))
    else:
        return redirect(url_for('usuario'))

    
@app.route('/usuario/delete/<int:id>/')
def delete(id):
    data = db_usuario.read(id);

    if len(data) == 0:
        return redirect(url_for('usuario'))
    else:
        session['delete'] = id
        return render_template('usuario/delete.html', data = data)
    
@app.route('/usuario/deleteusuario', methods = ['POST'])
def deleteusuario():
    if request.method == 'POST' and request.form['delete']:

        if db_usuario.delete(session['delete']):
            flash('Usuario eliminado')
        else:
            flash('ERROR al eliminar')
        session.pop('delete', None)

        return redirect(url_for('usuario'))
    else:
        return redirect(url_for('usuario'))

#----------------------------------------------------------------CLIENTES:----------------------------------------------------------------

@app.route("/cliente/")

def cliente():
    datos = db_cliente.read(None)
    logger.exception("Index de clientes")
    return render_template("cliente/index.html", data=datos)

@app.route('/cliente/add2/')

def add2():
    return render_template('cliente/add2.html')

@app.route('/cliente/addcliente', methods = ['POST', 'GET'])
def addcliente():
    if request.method == 'POST' and request.form['save']:
        if db_cliente.insert(request.form):
            flash("Nuevo cliente creado")
        else:
            flash("ERROR, al crear cliente")

        return redirect(url_for('cliente'))
    else:
        return redirect(url_for('cliente'))
    
@app.route('/cliente/update2/<int:id>/')
def update2(id):
    data = db_cliente.read(id)

    if len(data) == 0:
        return redirect(url_for('cliente'))
    else:
        session['update'] = id
        return render_template('cliente/update2.html', data = data)

@app.route('/cliente/updatecliente', methods = ['POST'])
def updatecliente():
    if request.method == 'POST' and request.form['update']:

        if db_cliente.update(session['update'], request.form):
            flash('Se actualizo correctamente')
        else:
            flash('ERROR en actualizar')

        session.pop('update', None)

        return redirect(url_for('cliente'))
    else:
        return redirect(url_for('cliente'))

@app.route('/cliente/delete2/<int:id>/')
def delete2(id):
    data = db_cliente.read(id);

    if len(data) == 0:
        return redirect(url_for('cliente'))
    else:
        session['delete'] = id
        return render_template('cliente/delete2.html', data = data)
    
@app.route('/cliente/deletecliente', methods = ['POST'])
def deletecliente():
    if request.method == 'POST' and request.form['delete']:

        if db_cliente.delete(session['delete']):
            flash('Cliente eliminado')
        else:
            flash('ERROR al eliminar')
        session.pop('delete', None)

        return redirect(url_for('cliente'))
    else:
        return redirect(url_for('cliente'))
    
#----------------------------------------------------------------CATEGORIAS----------------------------------------------------------------

@app.route("/categoria/")

def categoria():
    datos = db_categoria.read(None)
    return render_template("categoria/index.html", data=datos)

@app.route('/categoria/add3/')

def add3():
    return render_template('categoria/add3.html')

@app.route('/categoria/addcategoria', methods = ['POST', 'GET'])
def addcategoria():
    if request.method == 'POST' and request.form['save']:
        if db_categoria.insert(request.form):
            flash("Nueva categoria creada")
        else:
            flash("ERROR, al crear categoria")

        return redirect(url_for('categoria'))
    else:
        return redirect(url_for('categoria'))
    
@app.route('/categoria/update3/<int:id>/')
def update3(id):
    data = db_categoria.read(id)

    if len(data) == 0:
        return redirect(url_for('categoria'))
    else:
        session['update'] = id
        return render_template('categoria/update3.html', data = data)

@app.route('/categoria/updatecategoria', methods = ['POST'])
def updatecategoria():
    if request.method == 'POST' and request.form['update']:
        if db_categoria.update(session['update'], request.form):
            flash('Se actualizo correctamente')
        else:
            flash('ERROR en actualizar')

        session.pop('update', None)

        return redirect(url_for('categoria'))
    else:
        return redirect(url_for('categoria'))

@app.route('/categoria/delete3/<int:id>/')
def delete3(id):
    data = db_categoria.read(id);

    if len(data) == 0:
        return redirect(url_for('categoria'))
    else:
        session['delete'] = id
        return render_template('categoria/delete3.html', data = data)
    
@app.route('/categoria/deletecategoria', methods = ['POST'])
def deletecategoria():
    if request.method == 'POST' and request.form['delete']:

        if db_categoria.delete(session['delete']):
            flash('Categoría eliminada')
        else:
            flash('ERROR al eliminar')
        session.pop('delete', None)

        return redirect(url_for('categoria'))
    else:
        return redirect(url_for('categoria'))

#----------------------------------------------------------------PRODUCTO----------------------------------------------------------------
@app.route("/producto/")

def producto():
    datos = db_producto.read(None)
    return render_template("producto/index.html", data=datos)

@app.route('/producto/add4/')

def add4():
    return render_template('producto/add4.html')

@app.route('/producto/addproducto', methods = ['POST', 'GET'])
def addproducto():
    if request.method == 'POST' and request.form['save']:
        if db_producto.insert(request.form):
            flash("Nuevo producto creado")
        else:
            flash("ERROR, al crear producto")

        return redirect(url_for('producto'))
    else:
        return redirect(url_for('producto'))

@app.route('/producto/update4/<int:id>/')
def update4(id):
    data = db_producto.read(id)

    if len(data) == 0:
        return redirect(url_for('producto'))
    else:
        session['update'] = id
        return render_template('producto/update4.html', data = data)

@app.route('/producto/updateproducto', methods = ['POST'])
def updateproducto():
    if request.method == 'POST' and request.form['update']:
        if db_producto.update(session['update'], request.form):
            flash('Se actualizo correctamente')
        else:
            flash('ERROR en actualizar')

        session.pop('update', None)

        return redirect(url_for('producto'))
    else:
        return redirect(url_for('producto'))
    
@app.route('/producto/delete4/<int:id>/')
def delete4(id):
    data = db_producto.read(id);

    if len(data) == 0:
        return redirect(url_for('producto'))
    else:
        session['delete'] = id
        return render_template('producto/delete4.html', data = data)
    
@app.route('/producto/deleteproducto', methods = ['POST'])
def deleteproducto():
    if request.method == 'POST' and request.form['delete']:

        if db_producto.delete(session['delete']):
            flash('Producto eliminado')
        else:
            flash('ERROR al eliminar')
        session.pop('delete', None)

        return redirect(url_for('producto'))
    else:
        return redirect(url_for('producto'))
    
#----------------------------------------------------------------PEDIDOS----------------------------------------------------------------

@app.route("/pedido/")

def pedido():
    datos = db_pedido.read(None)
    return render_template("pedido/index.html", data=datos)

@app.route('/pedido/add5/')

def add5():
    return render_template('pedido/add5.html')

@app.route('/pedido/addpedido', methods = ['POST', 'GET'])
def addpedido():
    if request.method == 'POST' and request.form['save']:
        if db_pedido.insert(request.form):
            flash("Nuevo pedido creado")
        else:
            flash("ERROR, al crear pedido")

        return redirect(url_for('pedido'))
    else:
        return redirect(url_for('pedido'))

@app.route('/pedido/update5/<int:id>/')
def update5(id):
    data = db_pedido.read(id)

    if len(data) == 0:
        return redirect(url_for('pedido'))
    else:
        session['update'] = id
        return render_template('pedido/update5.html', data = data)

@app.route('/pedido/updatepedido', methods = ['POST'])
def updatepedido():
    if request.method == 'POST' and request.form['update']:
        if db_pedido.update(session['update'], request.form):
            flash('Se actualizo correctamente')
        else:
            flash('ERROR en actualizar')

        session.pop('update', None)

        return redirect(url_for('pedido'))
    else:
        return redirect(url_for('pedido'))

@app.route('/pedido/delete5/<int:id>/')
def delete5(id):
    data = db_pedido.read(id);

    if len(data) == 0:
        return redirect(url_for('pedido'))
    else:
        session['delete'] = id
        return render_template('pedido/delete5.html', data = data)
    
@app.route('/pedido/deletepedido', methods = ['POST'])
def deletepedido():
    if request.method == 'POST' and request.form['delete']:

        if db_pedido.delete(session['delete']):
            flash('Pedido eliminado')
        else:
            flash('ERROR al eliminar')
        session.pop('delete', None)

        return redirect(url_for('pedido'))
    else:
        return redirect(url_for('pedido'))


#----------------------------------------------------------------PAGINA PRINCIPAL----------------------------------------------------------------

@app.route('/')

def index_principal():
    
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    cursor = conn.cursor()

    # Ejecutar una consulta para obtener los primeros 4 productos
    cursor.execute('SELECT *FROM producto LIMIT 4')
    productos = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()

    # Renderizar la plantilla HTML con los resultados
    if 'logueado2' in session and session['logueado2']:
       return render_template("index_tienda.html", nombre_cliente=session['nombre_cliente'], apellido_cliente=session['apellido_cliente'], foto_cliente=session['foto_cliente'], dni_cliente=session['dni_cliente'], telefono_cliente=session['telefono_cliente'], correo_cliente=session['correo_cliente'],productos = productos)
    else:
       return render_template("index_tienda.html", productos=productos)
        

@app.route('/cerrar_sesion')
def cerrar_sesion():
    if 'logueado2' in session and session['logueado2']:
        # Solo limpia la sesión si el usuario ha iniciado sesión
        session.clear()
    return redirect(url_for('index_principal'))

@app.route('/store-cart')
def store_cart():
    return render_template('store-cart.html')

def quitar_porcentaje20(cadena):
    # Reemplazar '%20' con espacios en blanco
    cadena_sin_porcentaje20 = cadena.replace('%20', ' ')
    return cadena_sin_porcentaje20

def obtener_productos_aleatorios(cantidad=4):
    connection = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    cursor = connection.cursor()

    try:
        # Obtener el número total de filas en la tabla
        cursor.execute("SELECT COUNT(*) FROM producto")
        total_filas = cursor.fetchone()[0]

                # Obtener el número total de filas en la tabla
        cursor.execute("SELECT MAX(id) AS maximo_id, MIN(id) AS minimo_id FROM producto")
        resultado = cursor.fetchone()

        maximo_id = resultado[0]
        minimo_id = resultado[1]
        # Seleccionar filas aleatorias
        filas_aleatorias = random.sample( range(minimo_id, maximo_id),  min(cantidad, total_filas))

        # Construir la consulta SQL con los IDs seleccionados
        query = f"SELECT * FROM producto WHERE id IN ({','.join(map(str, filas_aleatorias))})"
        cursor.execute(query)
        cursor.close()
        connection.close()
        # Obtener los resultados
        productos_aleatorios = cursor.fetchall()

        return productos_aleatorios
    except Exception as e:
        print(f"Error al obtener productos aleatorios: {str(e)}")
        return []

@app.route("/<categoria>/<nombre>")
def store_product(categoria,nombre):
    productos_aleatorios = obtener_productos_aleatorios()
    juego = obtener_juegos_por_nombre(quitar_porcentaje20(nombre))
    return render_template('store-product.html', juego=juego,productos_aleatorios=productos_aleatorios)

def obtener_juegos_por_nombre(nombre):
    # Conectar a la base de datos
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    cursor = conn.cursor()

    try:
        # Realizar la consulta SQL para obtener los juegos de la categoría especificada
        query = "SELECT *FROM producto WHERE nombre = %s"
        cursor.execute(query, (nombre,))
        
        # Obtener los resultados de la consulta
        juego = cursor.fetchall()
        cursor.close()
        conn.close()
        return juego[0]
    except Exception as e:
        print(f"Error al obtener juego: {str(e)}")

@app.route('/pedidos')
def pedidos():
    return render_template('pedidos.html')

@app.route('/store')
def store():
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )
    cursor = conn.cursor()

    # Ejecutar una consulta para obtener los primeros 4 productos
    cursor.execute('SELECT * FROM producto LIMIT 16')
    productos = cursor.fetchall()

    # Cerrar la conexión con la base de datos
    conn.close()
    return render_template('store.html',productos=productos)

@app.route('/merchandising')
def merchandising():
    return render_template('merchandising.html')

@app.route('/merchandising-limit')
def merchandising_limit():
    return render_template('merchandising_limit.html')

def obtener_juegos_por_categoria(categoria):
    # Conectar a la base de datos
    conn = pymysql.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

    cursor = conn.cursor()

    try:
        # Realizar la consulta SQL para obtener los juegos de la categoría especificada
        query = "SELECT *FROM producto WHERE categorias = %s"
        cursor.execute(query, (categoria,))
        
        # Obtener los resultados de la consulta
        juegos = cursor.fetchall()
        cursor.close()
        conn.close()
        return juegos
    except Exception as e:
        print(f"Error al obtener juegos: {str(e)}")

@app.route('/store-catalog')
def store_catalog():
    return render_template('store-catalog.html')

@app.route('/<categoria>')
def juegos_por_categoria(categoria):
    juegos = obtener_juegos_por_categoria(categoria)
    return render_template('store-catalog-alt.html', categoria=categoria, juegos=juegos)

@app.route('/store-checkout')
def store_checkout():
    return render_template('store-checkout.html')

@app.route('/store-checkout-2')
def store_checkout_2():
    return render_template('store-checkout-2.html')

@app.route('/store-checkout-3')
def store_checkout_3():
    return render_template('store-checkout-succesful.html')

@app.route('/blog-list')
def blog_list():
    return render_template('blog-list.html')


@app.route('/control_panel')
def control_panel():
    return render_template('control_panel.html')


@app.route('/enviar_mensaje', methods=['POST', 'GET'])
def enviarmensaje():
    if request.method == 'POST' and 'save' in request.form:
        if db_mensaje.insert(request.form):
            flash("Mensaje enviado", 'success')  # Agrega la categoría 'success' para un mejor manejo en la plantilla
        else:
            flash("ERROR al enviar mensaje", 'error')  # Agrega la categoría 'error'

        return redirect(url_for('index_principal'))
    else:
        return redirect(url_for('index_principal'))

    
@app.route('/borrar_mensaje/<int:mensaje_id>', methods=['GET', 'POST'])
def deletemensaje(mensaje_id):
    if request.method == 'POST':
        if db_mensaje.delete(mensaje_id):
            flash("Mensaje Eliminado")
            return redirect(url_for('index'))
        else:
            flash('ERROR al eliminar')

    # Lógica para manejar GET (puedes redirigir o renderizar una plantilla, según sea necesario)
    return redirect(url_for('index'))



if __name__ == "__main__":
    app.run(debug=True,port=4000)