from flask import render_template, flash, redirect, url_for, request,Blueprint
from wtforms import Form, StringField, PasswordField, validators,SelectField, IntegerField
from auth import is_logged_in
from extensions import mysql
import numpy

bp = Blueprint('product', __name__)


# View Products
@bp.route('/products')
@is_logged_in
def products():

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM product")

    products = cur.fetchall()

    if result > 0:
        return render_template('products.html',products=products)
    else:
        msg = 'No Product Found'
        return render_template('products.html', msg=msg)

    cur.close()

#Product Form Class
class ProductForm(Form):
    product_id = StringField('PRODUCT_ID',[validators.DataRequired()])
    name = StringField('NAME',[validators.DataRequired()])


#Add Products
@bp.route('/add_product',methods=['GET', 'POST'])
@is_logged_in
def add_product():

    cur = mysql.connection.cursor()

    form = ProductForm(request.form)

    result = cur.execute("SELECT product_id FROM product ORDER BY product_id DESC")


    if result > 0:
        pid = cur.fetchone()

        form.product_id.data = numpy.base_repr(int(pid['product_id'], 36) + 1, 36)
    
    cur.close()

    if request.method == 'POST' and form.validate():
        product_id = form.product_id.data
        name = form.name.data

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM product WHERE product_id = %s",[product_id])

        if result > 0:
            flash('Product Id already exists','danger')
            return render_template('add_product.html', form = form)

        cur.execute("INSERT INTO product(product_id, name) VALUES(%s, %s)",(product_id, name))

        mysql.connection.commit()

        cur.close()

        flash('Product Added', 'success')

        return redirect(url_for('product.products'))

    return render_template('add_product.html', form = form)


#Edit Product
@bp.route('/edit_product/<string:id>',methods = ['GET', 'POST'])
@is_logged_in
def edit_product(id):

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM product WHERE product_id = %s",[id])
    product = cur.fetchone()
    cur.close()

    form = ProductForm(request.form)

    form.product_id.data = product['product_id']
    form.name.data = product['name']

    if request.method == 'POST' and form.validate():
        product_id = request.form['product_id']
        name = request.form['name'] 

        cur = mysql.connection.cursor()

        cur.execute("UPDATE product SET product_id = %s,name = %s WHERE product_id = %s",(product_id,name,id))
        
        mysql.connection.commit()

        cur.close()

        flash('Product Updated','success')

        return redirect(url_for('product.products'))
    
    return render_template('edit_product.html',form = form)


#Delete Product
@bp.route('/delete_product/<string:id>', methods=['POST'])
@is_logged_in
def delete_product(id):

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM product WHERE product_id = %s",[id])

    mysql.connection.commit()

    cur.close()

    flash('Product Deleted','success')

    return redirect(url_for('product.products'))