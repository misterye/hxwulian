# coding=utf-8
import sys;
# set the default encoding to utf-8
# reload sys model to enable the getdefaultencoding method.
reload(sys);
# using exec to set the excoding, to avoid error in IDE
exec("sys.setdefaultencoding('utf-8')");
assert sys.getdefaultencoding().lower() == "utf-8";
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import hashlib

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

# init MYSQL
mysql = MySQL(app)

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("未授权，请先登录。", 'danger')
            return redirect(url_for('login'))
    return wrap

# Check if user is admin
def is_admin(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session and session['username'] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("操作未授权！请以管理员身份登录。", 'danger')
            return redirect(url_for('login'))
    return wrap

# Register Form Class
class RegisterForm(Form):
    name = StringField('姓名', [validators.Length(min=1, max=50)])
    username = StringField('用户名', [validators.Length(min=4, max=30)])
    email = StringField('电子邮箱', [validators.Length(min=6, max=100)])
    password = PasswordField('密码', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='两次输入不匹配')
    ])
    confirm = PasswordField('确认密码')

# User Form Class
class UserForm(Form):
    name = StringField('姓名', [validators.Length(min=1, max=50)])
    username = StringField('用户名', [validators.Length(min=3, max=30)])
    email = StringField('电子邮箱', [validators.Length(min=6, max=100)])
    newPassword = PasswordField('新密码', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='两次输入不匹配')
    ])
    confirm = PasswordField('确认新密码')
	
# User Register
@app.route('/register', methods=['GET', 'POST'])
@is_admin
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))
        # Create cursor
        cur = mysql.connection.cursor()
        # Execute query
        cur.execute("INSERT INTO users(name, username, email, password) VALUES(%s, %s, %s, %s)", (name, username, email, password))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash("注册成功，请登录。", 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Index
@app.route('/')
@app.route('/index')
def index():
    return render_template('home.html')

# User login
#@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        username = request.form['username']
        password_candidate = request.form['password']
        # Create cursor
        cur = mysql.connection.cursor()
        # Get user by username
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])
        if result > 0:
            # Get stored hash
            data = cur.fetchone()
            password = data['password']
            name = data['name']
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username
                session['name'] = name
                return redirect(url_for('index'))
            else:
                error = "登录失败。"
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = "用户名不存在。"
            return render_template('login.html', error=error)
    return render_template('login.html')

# Logout
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    return redirect(url_for('login'))
	
# Dashboard_Users
@app.route('/dashboard_users')
#@is_logged_in
@is_admin
def dashboard_users():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM users ORDER BY id ASC")
    users = cur.fetchall()
    if result > 0:
        return render_template('dashboard_users.html', users=users)
    else:
        msg = 'No User Found'
        return render_template('dashboard_users.html', msg=msg)
    cur.close()
	
# Edit User
@app.route('/edit_user/<string:id>', methods=['GET', 'POST'])
#@is_logged_in
@is_admin
def edit_user(id):
    # Create cursor
    cur = mysql.connection.cursor()
    # Get user by id
    result = cur.execute("SELECT * FROM users WHERE id = %s", [id])
    user = cur.fetchone()
    # Get user
    form = UserForm(request.form)
    # Populate user form fields
    form.name.data = user['name']
    form.username.data = user['username']
    form.email.data = user['email']
    if request.method == 'POST' and form.validate():
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = sha256_crypt.encrypt(str(request.form['newPassword']))
        # Create cursor
        cur = mysql.connection.cursor()
        # Execute
        cur.execute("UPDATE users SET name=%s, username=%s, email=%s, password=%s WHERE id = %s", (name, username, email, password, id))
        # Commit to DB
        mysql.connection.commit()
        # Close connection
        cur.close()
        flash("用户更新成功。", 'success')
        return redirect(url_for('dashboard_users'))
    return render_template('edit_user.html', form=form)

# Delete User 
@app.route('/delete_user/<string:id>', methods=['POST'])
#@is_logged_in
@is_admin
def delete_user(id):
    # Create cursor
    cur = mysql.connection.cursor()
    # Execute
    cur.execute("DELETE FROM users WHERE id = %s", [id])
    # Commit to DB
    mysql.connection.commit()
    # Close connection
    cur.close()
    flash("用户删除成功。", 'success')
    return redirect(url_for('dashboard_users'))

@app.route('/chronograf')
@is_logged_in
def chronograf():
    return redirect("http://111.47.20.166:8888")

@app.route('/thinger')
@is_logged_in
def thinger():
    return redirect("http://111.47.20.166:8022")

@app.route('/nodered')
@is_logged_in
def nodered():
    return redirect("http://111.47.20.166:1880")

@app.route('/grafana')
@is_logged_in
def grafana():
    return redirect("http://111.47.20.166:3000")

if __name__ == '__main__':
    app.secret_key='fpaoiega84qddq48q0dijfe41fj0iggr9wrj'
    app.run('0.0.0.0', 8023)
