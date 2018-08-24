from flask import render_template, flash, redirect, url_for, request,Blueprint
from wtforms import Form, StringField, PasswordField, validators,SelectField, IntegerField
from extensions import mysql
from auth import is_logged_in
import numpy

bp = Blueprint('location', __name__)

# View Locations
@bp.route('/locations')
@is_logged_in
def locations():

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM location")

    locations = cur.fetchall()

    if result > 0:
        return render_template('locations.html',locations=locations)
    else:
        msg = 'No locations Found'
        return render_template('locations.html', msg=msg)

    cur.close()

#Location Form Class
class LocationForm(Form):
    location_id = StringField('LOCATION_ID',[validators.DataRequired()])
    lname = StringField('WAREHOUSE NAME',[validators.DataRequired()])


#Add Locations
@bp.route('/add_location',methods=['GET', 'POST'])
@is_logged_in
def add_location():

    cur = mysql.connection.cursor()

    form = LocationForm(request.form)

    result = cur.execute("SELECT location_id FROM location ORDER BY location_id DESC")


    if result > 0:
        lid = cur.fetchone()

        form.location_id.data = numpy.base_repr(int(lid['location_id'], 36) + 1, 36)
    
    cur.close()
    
    if request.method == 'POST' and form.validate():
        location_id = form.location_id.data
        lname = form.lname.data

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM location WHERE location_id = %s",[location_id])

        if result > 0:
            flash('Location Id already exists','danger')
            return render_template('add_location.html', form = form)

        cur.execute("INSERT INTO location(location_id, lname) VALUES(%s, %s)",(location_id, lname))
        
        mysql.connection.commit()

        cur.close()

        flash('Location Added', 'success')

        return redirect(url_for('location.locations'))

    return render_template('add_location.html', form = form)


#Edit Locations
@bp.route('/edit_location/<string:id>',methods = ['GET', 'POST'])
@is_logged_in
def edit_location(id):

    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM location WHERE location_id = %s",[id])
    location = cur.fetchone()
    cur.close()

    form = LocationForm(request.form)

    form.location_id.data = location['location_id']
    form.lname.data = location['lname']

    if request.method == 'POST' and form.validate():
        location_id = request.form['location_id']
        lname = request.form['lname'] 

        cur = mysql.connection.cursor()

        cur.execute("UPDATE location SET location_id = %s,lname = %s WHERE location_id = %s",(location_id,lname,id))
        
        mysql.connection.commit()

        cur.close()

        flash('Product Updated','success')

        return redirect(url_for('location.locations'))
    
    return render_template('edit_location.html',form = form)


#Delete Locations
@bp.route('/delete_location/<string:id>', methods=['POST'])
@is_logged_in
def delete_location(id):

    cur = mysql.connection.cursor()

    cur.execute("DELETE FROM location WHERE location_id = %s",[id])

    mysql.connection.commit()

    cur.close()

    flash('Location Deleted','success')

    return redirect(url_for('location.locations'))