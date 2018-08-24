from flask import render_template, flash, redirect, url_for, request,Blueprint
from wtforms import Form, StringField, PasswordField, validators,SelectField, IntegerField
from extensions import mysql
from auth import is_logged_in
import numpy

bp = Blueprint('movement', __name__)


# View Movement
@bp.route('/movements')
@is_logged_in
def movements():

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM movement")

    movements = cur.fetchall()

    if result > 0:
        return render_template('movements.html',movements=movements)
    else:
        msg = 'No Movements Found'
        return render_template('movements.html', msg=msg)

    cur.close()

# Get Report
@bp.route('/report')
@is_logged_in
def report():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM location")
    locations = cur.fetchall()
    r=[]

    for l in locations:
        
        cur.execute("SELECT * FROM product")
        products = cur.fetchall()

        for p in products:

            cur.execute("SELECT SUM(qty) from movement where from_loc = %s AND product_id = %s",(l['location_id'],p['product_id']))
            qty1 = cur.fetchone()

            cur.execute("SELECT SUM(qty) from movement where to_loc = %s AND product_id = %s",(l['location_id'],p['product_id']))
            qty2 = cur.fetchone()
            
            if qty1['SUM(qty)'] == None:
                qty1['SUM(qty)'] = int(0)
            
            if qty2['SUM(qty)'] == None:
                qty2['SUM(qty)'] = int(0)
            
            balance = int(qty2['SUM(qty)']) - int(qty1['SUM(qty)']) 

            r += [(p['name'],l['lname'],balance)]
             
    return render_template('report.html',result=r)

    cur.close()


#Form Class
class MoveProduct(Form):
    movement_id = StringField('MOVEMENT_ID',[validators.DataRequired()])
    from_loc = SelectField('FROM LOCATION',choices=[])
    to_loc = SelectField('TO LOCATION',choices=[],default='')
    product_id = SelectField('PRODUCT_ID',[validators.DataRequired()],choices=[])
    qty = IntegerField('QUANTITY',[validators.DataRequired()])


#Move Product
@bp.route('/move_product',methods=['GET','POST'])
@is_logged_in
def move_product():

    cur = mysql.connection.cursor()
    cur.execute("SELECT lname FROM location")
    location = cur.fetchall() 

    cur.execute("SELECT name FROM product")
    product = cur.fetchall()

    result = cur.execute("SELECT movement_id FROM movement ORDER BY timestamp DESC")
    
    form = MoveProduct(request.form)

    if result > 0:
        mid = cur.fetchone()

        form.movement_id.data = numpy.base_repr(int(mid['movement_id'], 36) + 1, 36)

    form.from_loc.choices = [("","")]+[(l['lname'],l['lname']) for l in location]  
    form.to_loc.choices = [("","")]+[(l['lname'],l['lname']) for l in location]
    form.product_id.choices = [(p['name'],p['name']) for p in product]


    cur.close()
    
    if request.method == 'POST' and form.validate():
        movement_id = request.form['movement_id']
        from_loc = form.from_loc.data
        to_loc = form.to_loc.data
        product_id = form.product_id.data
        qty = form.qty.data

        cur = mysql.connection.cursor()

        if(from_loc):
            cur.execute("SELECT location_id FROM location WHERE lname = %s",[from_loc])
            result = cur.fetchone()
            from_loc = result['location_id']

        if(to_loc):
            cur.execute("SELECT location_id FROM location WHERE lname = %s",[to_loc])
            result = cur.fetchone()
            to_loc = result['location_id']

        cur.execute("SELECT product_id FROM product WHERE name = %s",[product_id])
        result = cur.fetchone()
        product_id = result['product_id']

        if validMove(from_loc,to_loc,product_id,qty):
            

            cur.execute("INSERT INTO movement(movement_id,from_loc,to_loc,product_id,qty) VALUES(%s, %s, %s, %s, %s)",(movement_id, from_loc, to_loc, product_id, qty))

            mysql.connection.commit()

            cur.close()

            flash('Product Moved', 'success')

            return redirect(url_for('movement.movements'))

    return render_template('move_product.html', form = form)


#Edit Product
@bp.route('/edit_movement/<string:id>',methods = ['GET', 'POST'])
@is_logged_in
def edit_movement(id):

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM movement WHERE movement_id = %s",[id])
    movement = cur.fetchone()

    cur.execute("SELECT * FROM location")
    location = cur.fetchall() 

    cur.execute("SELECT * FROM product")
    product = cur.fetchall()

    cur.close()

    form = MoveProduct(request.form)

    form.from_loc.choices = [("","")]+[(l['location_id'],l['lname']) for l in location]  
    form.to_loc.choices = [("","")]+[(l['location_id'],l['lname']) for l in location]
    form.product_id.choices = [(p['product_id'],p['name']) for p in product]


    form.from_loc.default = movement['from_loc']
    form.to_loc.default= movement['to_loc']
    form.product_id.default = movement['product_id']
    form.process()

    form.movement_id.data = movement['movement_id']
    form.qty.data = movement['qty']


    if request.method == 'POST' and form.validate():
        movement_id = request.form['movement_id']
        from_loc = request.form['from_loc']
        to_loc = request.form['to_loc']
        product_id = request.form['product_id']
        qty = request.form['qty']
        

        cur = mysql.connection.cursor()

        cur.execute("UPDATE movement SET movement_id = %s,from_loc = %s,to_loc = %s,product_id = %s,qty = %s WHERE movement_id = %s",(movement_id,from_loc,to_loc,product_id,qty,id))
        
        mysql.connection.commit()

        cur.close()

        flash('Movement Updated','success')

        return redirect(url_for('movement.movements'))
    
    return render_template('edit_movement.html',form = form)


#Validate Move
def validMove(from_loc,to_loc,product_id,qty):

    cur = mysql.connection.cursor()

    if from_loc == to_loc:
        flash('Both from and to cannot be same', 'danger')
        return False

    elif(from_loc):

        cur.execute("SELECT SUM(qty) from movement where from_loc = %s AND product_id = %s",(from_loc,product_id))
        qty1 = cur.fetchone()

        cur.execute("SELECT SUM(qty) from movement where to_loc = %s AND product_id = %s",(from_loc,product_id))
        qty2 = cur.fetchone()

        

        if qty1['SUM(qty)'] == None:
            qty1['SUM(qty)'] = int(0)
        
        if qty2['SUM(qty)'] == None:
            qty2['SUM(qty)'] = int(0)
        

        if int(qty2['SUM(qty)']) - int(qty1['SUM(qty)']) >= qty :
             return True
        else:
             flash('Not Enough Quantity In From Location', 'danger')
             return False
    elif not(from_loc) and not(to_loc):
        flash('Both from and to cannot be empty', 'danger')
        return False

    elif from_loc == to_loc:
        flash('Both from and to cannot be same', 'danger')
        return False  

    cur.close()

    return True