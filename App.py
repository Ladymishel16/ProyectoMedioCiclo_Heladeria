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











if __name__ == '__main__':
    app.run(port=5000, debug=True)
