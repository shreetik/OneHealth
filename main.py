from asyncio.windows_events import NULL
from distutils.log import debug
from email import message
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_recaptcha import ReCaptcha
from requests import post
from flask_mail import Mail, Message
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'onehealth.noreply@gmail.com',
    "MAIL_PASSWORD": 'kejubbtuazirmqpw'
}
app.config.update(mail_settings)
mail = Mail(app)

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


@ app.route('/user/<string:cuser>')
def userpanel(cuser):
    if 'user_name' in session:
        cursor.execute(
            """SELECT * FROM `appointment_tbl` WHERE `patient_name` LIKE '{}' AND `deleted_by` LIKE '{}'""".format(cuser, '-'))
        active = cursor.fetchall()
        activeC = len(active)
        cursor.execute(
            """SELECT * FROM `appointment_tbl` WHERE `patient_name` LIKE '{}' AND `deleted_by` NOT LIKE '{}'""".format(cuser, '-'))
        canceled = cursor.fetchall()
        canceledC = len(canceled)
        return render_template('userdashboard.html', name=session['user_name'], activeC=activeC, canceledC=canceledC)
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


@ app.route('/view_patient')
def viewuser():
    cursor.execute("""SELECT * FROM `user`""")
    data = cursor.fetchall()
    if 'user_name' in session:
        return render_template('view_patients.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


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
            user = session['user_name']
            return redirect("/user/{}".format(user))
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


@ app.route('/adminhome')
def admindash():
    if 'user_name' in session:
        cursor.execute("""SELECT * FROM `doctor_tbl`""")
        doctor = cursor.fetchall()
        dcount = len(doctor)
        cursor.execute("""SELECT * FROM `user`""")
        user = cursor.fetchall()
        ucount = len(user)
        cursor.execute("""SELECT * FROM `appointment_tbl`""")
        active = cursor.fetchall()
        activeC = len(active)
        return render_template('adminDashboard.html', name=session['user_name'], dcount=dcount, ucount=ucount, activeC=activeC)
    else:
        return redirect('/adminLogin')


@ app.route('/validateAdmin_login', methods=['POST'])
def validateAdminLogin():
    if recaptcha.verify():
        email = request.form.get('txtmail')
        password = request.form.get('txtpass')

        cursor.execute(
            """SELECT * FROM `admin_tbl` WHERE `email` LIKE '{}' AND `password` LIKE '{}'""".format(email, password))
        user = cursor.fetchall()

        if len(user) > 0:
            session['user_name'] = user[0][1]
            return redirect('/adminhome')
        else:
            flash(f"Invalid user credentials", "error")
            return redirect('/adminLogin')

        return "{}{}".format(email, password)
    else:
        message = "Please fill out the ReCaptcha!"
        return render_template('admin_login.html', message=message)


@ app.route('/add_doctor')
def addDoctor():
    if 'user_name' in session:
        return render_template('createDoctor.html', name=session['user_name'])
    else:
        return redirect('/adminLogin')


@ app.route('/create_doctor', methods=['POST'])
def createDoctor():
    dname = request.form.get('dname')
    fullname = 'Dr.'+' '+dname
    email = request.form.get('txtemail')
    phone = request.form.get('txtno')
    spec = request.form.get('selectspec')
    fee = request.form.get('txtfee')
    password = request.form.get('txtpass')

    cursor.execute("""INSERT INTO `doctor_tbl` (`id`,`doctor_name`,`phone_no`,`email`,`specalization`,`fee`,`password`) VALUES(NULL,'{}','{}','{}','{}','{}','{}')""".format(
        fullname, phone, email, spec, fee, password))

    conn.commit()
    if cursor.rowcount == 1:
        flash(f"Doctor added Succesfully", "success")
    else:
        flash(f"Server Error", "danger")

    return redirect('/add_doctor')


@ app.route('/view_doctor')
def viewdoctor():
    cursor.execute("""SELECT * FROM `doctor_tbl`""")
    data = cursor.fetchall()

    if 'user_name' in session:
        return render_template('view_doctor.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


@ app.route('/adminsideapp')
def viewtotalapp():
    cursor.execute("""SELECT * FROM `appointment_tbl`""")
    data = cursor.fetchall()

    if 'user_name' in session:
        return render_template('adminSideApp.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


@ app.route('/edit_doctor/<int:id>')
def editdoctor(id):

    cursor.execute(
        """SELECT * FROM `doctor_tbl` WHERE `id` LIKE '{}'""".format(id))
    data = cursor.fetchall()

    if 'user_name' in session:
        return render_template('edit_doctor.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


@ app.route('/update_doctor/<int:id>', methods=['POST'])
def updatedoctor(id):

    dname = request.form.get('dname')
    email = request.form.get('txtemail')
    phone = request.form.get('txtno')
    spec = request.form.get('selectspec')
    fee = request.form.get('txtfee')
    password = request.form.get('txtpass')

    cursor.execute(
        """UPDATE `doctor_tbl` SET `doctor_name`='{}', `phone_no`='{}',`email`='{}',`specalization`='{}',`fee`='{}',`password`='{}'  WHERE `id`={} """.format(dname, phone, email, spec, fee, password, id))
    conn.commit()
    if cursor.rowcount == 1:
        flash(f"Doctor Updated Succesfully", "success")
        return redirect('/view_doctor')
    else:
        flash(f"Server Error", "danger")
        return redirect("/edit_doctor/{}".format(id))


@ app.route('/delete_doctor/<int:id>')
def deletedoctor(id):

    cursor.execute(
        """DELETE FROM `doctor_tbl` WHERE `id`={}""".format(id))
    conn.commit()

    if cursor.rowcount == 1:
        flash(f"One Doctor Deleted Succesfully", "success")
        return redirect('/view_doctor')
    else:
        flash(f"Server Error", "danger")
        return redirect('/view_doctor')


@ app.route('/app_booking')
def appbooking():
    if 'user_name' in session:
        return render_template('appbooking.html', name=session['user_name'])
    else:
        return redirect('/login')


@ app.route('/bookapp/<string:dept>')
def bookappbycat(dept):
    print(dept)
    cursor.execute(
        """SELECT * FROM `doctor_tbl` WHERE `specalization` LIKE '{}'""".format(dept))
    data = cursor.fetchall()

    if 'user_name' in session:
        return render_template('bookappbycat.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


@ app.route('/saveapp/<string:user>', methods=['POST'])
def saveapp(user):
    spec = request.form.get('txtdept')
    dname = request.form.get('txtname')
    fee = request.form.get('txtfee')
    date = request.form.get('txtdate')
    time = request.form.get('txttime')

    cursor.execute("""INSERT INTO `appointment_tbl` (`appointment_id`,`patient_name`,`doctor_name`,`specalization`,`fee`,`date`,`time`,`status`,`deleted_by`) VALUES(NULL,'{}','{}','{}','{}','{}','{}','{}','{}')""".format(
        user, dname, spec, fee, date, time, 'ACTIVE', '-'))

    conn.commit()
    if cursor.rowcount == 1:
        flash(f"Appointment Booked Successfully", "success")
    else:
        flash(f"Server Error", "danger")

    return redirect("/app_booking")


@ app.route('/apphistory/<string:user>')
def apphistory(user):

    cursor.execute(
        """SELECT * FROM `appointment_tbl` WHERE `patient_name` LIKE '{}' AND `deleted_by` LIKE '{}'""".format(user, '-'))
    data = cursor.fetchall()
    print(data)
    if 'user_name' in session:
        return render_template('userapphistory.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


@ app.route('/apphistorycanceled/<string:user>')
def cancelhistory(user):

    cursor.execute(
        """SELECT * FROM `appointment_tbl` WHERE `patient_name` LIKE '{}' AND `deleted_by` NOT LIKE '{}'""".format(user, '-'))
    data = cursor.fetchall()
    print(data)
    if 'user_name' in session:
        return render_template('canceledApphistory.html', name=session['user_name'], data=data)
    else:
        return redirect('/adminLogin')


@ app.route('/cancelAppByUser/<int:id>/<string:user>')
def appcancel(id, user):

    cursor.execute(
        """UPDATE `appointment_tbl` SET `deleted_by`='{}',`status`='{}' WHERE `appointment_id`={} """.format('User', 'CANCELED', id))
    conn.commit()
    if cursor.rowcount == 1:
        flash(f"Appointment Canceled Successfully", "success")
        return redirect("/apphistory/{}".format(user))
    else:
        flash(f"Server Error", "danger")
        return redirect("/apphistory/{}".format(user))


@ app.route('/forgot_Password')
def forgotpass():
    return render_template('forgotPassword.html')


@app.route("/sentmail", methods=['POST'])
def index():

    try:
        email = request.form.get('txtmail')
        cursor.execute(
            """SELECT `password` FROM `user` WHERE `email_id` LIKE '{}'""".format(email))
        password = cursor.fetchone()
        msg = Message(
            'Your Onehealth Login Password',
            sender='Onehealth',
            recipients=[email]
        )
        #msg.body = "Password : '{}'".format(password[0])
        msg.html = "<h1 style='display:inline-block'>Password : </h1>&nbsp;<h1 style='color:green;display:inline-block'>{}</h1>".format(
            password[0])
        mail.send(msg)

        flash(f"Please check your email", "success")
        return redirect('/forgot_Password')

    except:
        flash(f"Invalid email", "error")
        return redirect('/forgot_Password')


@ app.route('/vd')
def forg():
    return render_template('view_patients.html')


if __name__ == "__main__":
    app.run(debug=True)


#

#
