from distutils.log import debug
from flask import Flask, render_template
from flask_recaptcha import ReCaptcha

app = Flask(__name__)
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


if __name__ == "__main__":
    app.run(debug=True)


#

#
