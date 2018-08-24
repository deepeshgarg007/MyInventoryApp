from flask import Flask, render_template, flash, redirect, url_for, request,Blueprint
import product
import location
import movement
import auth
from extensions import mysql


app = Flask(__name__)

app.register_blueprint(product.bp)
app.register_blueprint(location.bp)
app.register_blueprint(movement.bp)
app.register_blueprint(auth.bp)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'myFlaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql.init_app(app)


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)