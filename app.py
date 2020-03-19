from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = 'verysecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route('/', methods=['GET'])
def index():

    return redirect('register')


@app.route('/register', methods=['GET', 'POST'])
def handle_register_form():

    form = RegisterForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        try:
            user = User.register(username, password, email,
                                 first_name, last_name)
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            flash('Username already taken')
            return redirect('/')

        session['user'] = user.username

        return redirect(f'/users/{session["user"]}')

    else:
        return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def handle_login():

    form = LoginForm()

    if form.validate_on_submit():

        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            session["user"] = user.username
            return redirect(f'/users/{session["user"]}')
        else:
            form.username.errors = ['Invalid username or password']

    return render_template('login.html', form=form)


@app.route('/users/<string:username>', methods=['GET'])
def show_user(username):

    if session['user'] != username:
        flash('Please log in first!')
        return redirect('/login')

    user = User.query.get(username)

    return render_template('user.html', user=user)


@app.route('/logout', methods=['GET'])
def handle_logout():

    session.pop("user")

    return redirect('/')
