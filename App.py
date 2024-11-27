from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
import MySQLdb.cursors, base64





app = Flask(__name__, template_folder="templates")

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'duki'
app.config['MYSQL_DB'] = 'Heladeria'

mysql = MySQL(app)
app.secret_key = 'mysecretkey'

@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/principal')
def Principal():
    return render_template('principal.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

# ----------- CRUD para Categorías -----------
# Mostrar todas las categorías
@app.route('/categorias')
def categorias():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Categorias')
    categorias = cur.fetchall()
    return render_template('add_Categorias.html', categorias=categorias)

# Agregar una nueva categoría
@app.route('/add_Categorias', methods=['POST'])
def add_Categorias():
    categoria_nombre = request.form['categoria_nombre']
    description = request.form['description']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO Categorias (categoria_nombre, description) VALUES (%s, %s)', (categoria_nombre, description))
    mysql.connection.commit()
    flash('Categoría agregada correctamente')
    return redirect(url_for('categorias'))

# Actualizar categoría
@app.route('/edit_Categoria/<int:id>', methods=['POST', 'GET'])
def edit_Categoria(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Categorias WHERE category_id = %s', [id])
    categoria = cur.fetchone()
    if request.method == 'POST':
        categoria_nombre = request.form['categoria_nombre']
        description = request.form['description']
        cur.execute("""
            UPDATE Categorias
            SET categoria_nombre = %s, description = %s
            WHERE category_id = %s
        """, (categoria_nombre, description, id))
        mysql.connection.commit()
        flash('Categoría actualizada correctamente')
        return redirect(url_for('categorias'))
    return render_template('edit_Categorias.html', categoria=categoria)

# Eliminar categoría
@app.route('/delete_Categoria/<int:id>', methods=['GET'])
def delete_Categoria(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Categorias WHERE category_id = %s', [id])
    mysql.connection.commit()
    flash('Categoría eliminada correctamente')
    return redirect(url_for('categorias'))
#----------------------------------------------

# ----------- CRUD para Pedidos -----------
# Mostrar todos los pedidos
@app.route('/pedidos')
def pedidos():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Pedidos')
    pedidos = cur.fetchall()
    return render_template('add_Pedidos.html', pedidos=pedidos)

# Agregar un nuevo pedido
@app.route('/add_Pedidos', methods=['POST'])
def add_Pedidos():
    fecha_pedido = request.form['fecha_pedido']
    customer_id = request.form['customer_id']
    precio_total = request.form['precio_total']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO Pedidos (fecha_pedido, customer_id, precio_total) VALUES (%s, %s, %s)', 
                (fecha_pedido, customer_id, precio_total))
    mysql.connection.commit()
    flash('Pedido agregado correctamente')
    return redirect(url_for('pedidos'))

# Actualizar pedido
@app.route('/edit_Pedido/<int:id>', methods=['POST', 'GET'])
def edit_Pedido(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Pedidos WHERE order_id = %s', [id])
    pedido = cur.fetchone()
    if request.method == 'POST':
        fecha_pedido = request.form['fecha_pedido']
        customer_id = request.form['customer_id']
        precio_total = request.form['precio_total']
        cur.execute("""
            UPDATE Pedidos
            SET fecha_pedido = %s, customer_id = %s, precio_total = %s
            WHERE order_id = %s
        """, (fecha_pedido, customer_id, precio_total, id))
        mysql.connection.commit()
        flash('Pedido actualizado correctamente')
        return redirect(url_for('pedidos'))
    return render_template('edit_Pedidos.html', pedido=pedido)

# Eliminar pedido
@app.route('/delete_Pedido/<int:id>', methods=['GET'])
def delete_Pedido(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Pedidos WHERE order_id = %s', [id])
    mysql.connection.commit()
    flash('Pedido eliminado correctamente')
    return redirect(url_for('pedidos'))
#----------------------------------------------

# ----------- CRUD para Productos -----------
# Mostrar todos los productos

@app.route('/productos')
def productos():
    cur = mysql.connection.cursor()
    
    # Consulta ajustada para incluir el nombre de la categoría
    cur.execute('''
        SELECT 
            Productos.id, 
            Productos.nombre, 
            Productos.precio, 
            Productos.imagen, 
            Productos.descripcion, 
            Categorias.categoria_nombre 
        FROM 
            Productos
        LEFT JOIN 
            Categorias 
        ON 
            Productos.categoria = Categorias.category_id
    ''')
    
    productos = cur.fetchall()
    cur1 = mysql.connection.cursor()
    cur1.execute('SELECT category_id, categoria_nombre FROM Categorias')
    categorias = cur1.fetchall()
    # Procesar los productos para convertir la imagen a Base64 y organizar los datos
    productos_con_imagen = []
    for producto in productos:
        productos_con_imagen.append({
            'id': producto[0],  # id del producto
            'nombre': producto[1],  # nombre del producto
            'precio': producto[2],  # precio
            'imagen': base64.b64encode(producto[3]).decode('utf-8') if producto[3] else None,  # imagen en Base64
            'descripcion': producto[4],  # descripción
            'categoria_nombre': producto[5]  # nombre de la categoría
        })

    # Pasar los datos al template
    return render_template('add_Productos.html', productos=productos_con_imagen,categorias=categorias)


# Agregar un nuevo producto
@app.route('/add_Productos', methods=['POST'])
def add_Productos():
    # Si el método es POST, procesamos el formulario
    if request.method == 'POST':
        # Recoger datos del formulario
        producto_nombre = request.form['producto_nombre']
        producto_precio = request.form['producto_precio']
        producto_descripcion = request.form['producto_descripcion']
        category_id = request.form['category_id']  # Recoger el ID de la categoría seleccionada
        
        # Manejar la imagen (si existe)
        producto_imagen = None
        if 'producto_imagen' in request.files:
            file = request.files['producto_imagen']
            if file and file.filename != '':
                producto_imagen = file.read()  # Leer el archivo como binario
        
        # Insertar datos en la base de datos
        try:
            cur = mysql.connection.cursor()
            cur.execute(
                'INSERT INTO Productos (nombre, precio, descripcion, categoria, imagen) VALUES (%s, %s, %s, %s, %s)',
                (producto_nombre, producto_precio, producto_descripcion, category_id, producto_imagen)
            )
            mysql.connection.commit()
            flash('Producto agregado correctamente')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al agregar producto: {str(e)}')

        return redirect(url_for('productos'))

    
    

@app.route('/edit_Producto/<int:id>', methods=['POST', 'GET'])
def edit_Producto(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Productos WHERE id = %s', [id])
    producto = cur.fetchone()
    cur1 = mysql.connection.cursor()
    cur1.execute('SELECT category_id, categoria_nombre FROM Categorias')
    categorias = cur1.fetchall()
    categoria_actual = producto[6]  # Asegúrate de que esto sea el índice correcto

    if request.method == 'POST':
        producto_nombre = request.form['producto_nombre']
        producto_precio = request.form['producto_precio']
        producto_descripcion = request.form['producto_descripcion']
        category_id = request.form['category_id']
        
        # Manejo de la imagen
        producto_imagen = None
        if 'producto_imagen' in request.files:
            file = request.files['producto_imagen']
            if file and file.filename != '':
                producto_imagen = file.read()

        # Actualización del producto
        cur.execute("""
            UPDATE Productos
            SET nombre = %s, precio = %s, descripcion = %s, categoria = %s, imagen = %s
            WHERE id = %s
        """, (producto_nombre, producto_precio, producto_descripcion, category_id, producto_imagen, id))
        
        mysql.connection.commit()
        flash('Producto actualizado correctamente')
        return redirect(url_for('productos'))

    return render_template('edit_Productos.html', producto=producto, categorias=categorias, categoria_actual=categoria_actual)


# Eliminar producto
@app.route('/delete_Producto/<int:id>', methods=['GET'])
def delete_Producto(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Productos WHERE id = %s', [id])
    mysql.connection.commit()
    flash('Producto eliminado correctamente')
    return redirect(url_for('productos'))
#----------------------------------------------

# ------------ FUNCIONES CON CLIENTE -----------
@app.route('/add_Clientes')
def registro():
    return render_template('add_Clientes.html')  

@app.route('/crear-registro', methods=['GET','POST'])
def crear_registro():
    nombre = request.form['txtNombre']
    correo = request.form['txtCorreo']
    telefono = request.form['txtTelefono']
    direccion = request.form['txtDireccion']
    contraseña = request.form['txtContraseña']
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO Clientes   (nombre, correo, telefono, direccion, contraseña, id_rol) VALUES (%s, %s, %s, %s, %s, "2")', (nombre, correo, telefono, direccion, contraseña))
    mysql.connection.commit()
    flash('Cliente agregado correctamente')
    return redirect(url_for('Index'))

# ACCESO---LOGIN
@app.route('/acceso-login', methods= ['GET', 'POST'])
def acceso_login():
   
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtContraseña' in request.form:
       
        _correo = request.form['txtCorreo']
        _password = request.form['txtContraseña']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM clientes WHERE correo = %s AND contraseña = %s', (_correo, _password,))
        account = cur.fetchone()
      
        if account:
            session['logueado'] = True
            session['id'] = account['customer_id']
            session['id_rol']=account['id_rol']
            
            if session['id_rol']==1:
                return render_template('menu.html')
            elif session ['id_rol']==2:
                return render_template('principal.html')
        else:
            return render_template('index.html',mensaje="Usuario O Contraseña Incorrectas")
    return redirect(url_for('Index'))

@app.route('/clientes')
def list_Clientes():
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Clientes')
    clientes = cur.fetchall()
    return render_template('list_Clientes.html', clientes=clientes)

# Actualizar cliente
@app.route('/edit_Cliente/<int:id>', methods=['POST', 'GET'])
def edit_Cliente(id):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM Clientes WHERE customer_id = %s', [id])
    cliente = cur.fetchone()
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        telefono = request.form['telefono']
        direccion = request.form['direccion']
        cur.execute("""
            UPDATE Clientes
            SET nombre = %s, correo = %s, telefono = %s, direccion = %s
            WHERE customer_id = %s
        """, (nombre, correo, telefono, direccion, id))
        mysql.connection.commit()
        flash('Cliente actualizado correctamente')
        return redirect(url_for('list_Clientes'))
    return render_template('edit_Cliente.html', cliente=cliente)

# Eliminar cliente
@app.route('/delete_Cliente/<int:id>', methods=['GET'])
def delete_Cliente(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM Clientes WHERE customer_id = %s', [id])
    mysql.connection.commit()
    flash('Cliente eliminado correctamente')
    return redirect(url_for('list_Clientes'))
#----------------------------------------------

@app.route('/productos_cliente')
def productos_cliente():
    cur = mysql.connection.cursor()
    
    # Consulta para obtener los productos, incluyendo su imagen (en formato base64 si es necesario)
    cur.execute('''
        SELECT 
            Productos.id, 
            Productos.nombre, 
            Productos.precio, 
            Productos.imagen, 
            Productos.descripcion, 
            Categorias.categoria_nombre 
        FROM 
            Productos
        LEFT JOIN 
            Categorias 
        ON 
            Productos.categoria = Categorias.category_id
    ''')
    
    productos = cur.fetchall()

    # Procesar los productos para convertir la imagen a Base64 si es necesario
    productos_con_imagen = []
    for producto in productos:
        productos_con_imagen.append({
            'id': producto[0],
            'nombre': producto[1],
            'precio': producto[2],
            'imagen': base64.b64encode(producto[3]).decode('utf-8') if producto[3] else None,
            'descripcion': producto[4],
            'categoria_nombre': producto[5]
        })

    # Pasar los productos al template
    return render_template('productos_cliente.html', productos=productos_con_imagen)




@app.route('/producto_detalle/<int:id>')
def producto_detalle(id):
    cur = mysql.connection.cursor()
    cur.execute('''
        SELECT 
            Productos.id, 
            Productos.nombre, 
            Productos.precio, 
            Productos.imagen, 
            Productos.descripcion, 
            Categorias.categoria_nombre 
        FROM 
            Productos
        LEFT JOIN 
            Categorias 
        ON 
            Productos.categoria = Categorias.category_id
        WHERE Productos.id = %s
    ''', [id])
    
    producto = cur.fetchone()
    if producto:
        producto_detalle = {
            'id': producto[0],
            'nombre': producto[1],
            'precio': producto[2],
            'imagen': base64.b64encode(producto[3]).decode('utf-8') if producto[3] else None,
            'descripcion': producto[4],
            'categoria_nombre': producto[5]
        }
        return render_template('producto_detalle.html', producto=producto_detalle)
    return redirect(url_for('productos_cliente'))  # Redirigir si no se encuentra el producto


if __name__ == '__main__':
    app.run(port=5000, debug=True)
