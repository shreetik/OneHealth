from asyncio.windows_events import NULL
from distutils.log import debug
from email import message
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_recaptcha import ReCaptcha
from requests import post
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
conn = NULL
try:
    conn = mysql.connector.connect(host="localhost", user="root",
                                   password="root", database="onehealth", auth_plugin='mysql_native_password')
except:
    print("error")

cursor = conn.cursor()

app.config['RECAPTCHA_SITE_KEY'] = '6LdQ4DwgAAAAAACoU2jSbZUSR4Fvi6CySiJ75BFx'
app.config['RECAPTCHA_SECRET_KEY'] = '6LdQ4DwgAAAAAFxykuQHImTwFb8fcpPLLwSpe8O4'

recaptcha = ReCaptcha(app)


@app.route('/')
def home():
    return render_template('index.html')


@ app.route('/signup')
def signup():
    return render_template('signup.html')


@ app.route('/login')
def login():
    return render_template('login.html')


@ app.route('/doctorLogin')
def doctorlogin():
    return render_template('doctor_login.html')


@ app.route('/adminLogin')
def adminlogin():
    return render_template('admin_login.html')


@ app.route('/user')
def userpanel():
    if 'user_name' in session:
        return render_template('userdashboard.html')
    else:
        return redirect('/login')


@ app.route('/createuser', methods=['POST'])
def createUser():
    fname = request.form.get('fname')
    uname = request.form.get('uname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    password = request.form.get('password')
    gender = request.form.get('gender')

    cursor.execute(
        """SELECT * FROM `user` WHERE `email_id` LIKE '{}' """.format(email))
    user = cursor.fetchall()

    if len(user) == 0:

        cursor.execute("""INSERT INTO `user` (`user_id`,`full_name`,`user_name`,`email_id`,`phone_no`,`gender`,`password`) VALUES(NULL,'{}','{}','{}','{}','{}','{}')""".format(
            fname, uname, email, phone, gender, password))

        conn.commit()

        if cursor.rowcount == 1:
            flash(f"Account Succesfully created", "success")
        else:
            flash(f"Server Error", "danger")

        return redirect('/signup')

    else:
        flash(f"User already present", "warning")

        return redirect('/signup')


@ app.route('/validate_login', methods=['POST'])
def validateLogin():
    if recaptcha.verify():
        email = request.form.get('txtmail')
        password = request.form.get('txtpass')

        cursor.execute(
            """SELECT * FROM `user` WHERE `email_id` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
        user = cursor.fetchall()

        if len(user) > 0:
            session['user_name'] = user[0][2]
            return redirect('/user')
        else:
            flash(f"Invalid user credentials", "error")
            return redirect('/login')

        return "{}{}".format(email, password)
    else:
        message = "Please fill out the ReCaptcha!"
        return render_template('login.html', message=message)


@ app.route('/logout')
def logout():
    session.pop('user_name')
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)


#

#
