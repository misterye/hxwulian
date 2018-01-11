
# coding=utf-8
from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
from wtforms import Form, StringField, validators
import os
from flask_mail import Mail
from flask_mail import Message
from threading import Thread

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')
app.config.update(
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.exmail.qq.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = 'service@satelc.com',
    MAIL_PASSWORD = 'Bin*ping2252266'
    )

mysql = MySQL(app)
mail = Mail(app)

class AddForm(Form):
    content = StringField('内容', [validators.Length(min=1, max=255)])

@app.route('/')
def index():
    username = 'yebin'
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM todo WHERE user=%s AND complete IS FALSE ORDER BY id DESC", [username])
    incomplete = cur.fetchall()
    result = cur.execute("SELECT * FROM todo WHERE user=%s AND complete IS TRUE ORDER BY id DESC", [username])
    complete = cur.fetchall()
    if result > 0:
        return render_template('index.html', incomplete=incomplete, complete=complete)
    else:
        msg = "No todo list."
        return render_template('index.html', incomplete=incomplete, complete=complete)
    cur.close()

@app.route('/add', methods=['POST'])
def add():
    form = AddForm(request.form)
    username = 'yebin'
    if request.method == 'POST' and form.validate():
        content = form.content.data
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO todo(content, user) VALUES(%s, %s)", (content, username))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('index'))

@app.route('/complete/<id>')
def complete(id):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE todo SET complete=TRUE WHERE id=%s", [id])
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('index'))

# The following is sending email functions
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients):
    msg = Message(subject=subject, sender=sender, recipients=recipients)
    msg.html = "<b>TESTING</b>"
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()

@app.route('/send')
def send():
    send_email("This is a email sending test.", 'service@satelc.com', ['alert@satelc.com'])
    return 'Sent!'

if __name__ == '__main__':
    app.run('0.0.0.0', 8021)
