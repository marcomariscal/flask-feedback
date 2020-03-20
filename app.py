from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
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


@app.route('/users/<string:username>/delete')
def delete_user(username):

    if session["user"] != username:
        flash("You don't have permission to do that!")
        return redirect('/login')

    session.pop("user")

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()

    return redirect('/')


@app.route('/users/<string:username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):

    if session["user"] != username:
        flash("You don't have permission to do that!")
        return redirect('/login')

    user = User.query.get_or_404(username)

    form = FeedbackForm()

    if form.validate_on_submit():

        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()

        return redirect(f'/users/{username}')

    else:

        return render_template('feedback_add.html', form=form, user=user)


@app.route('/feedback/<int:feedback_id>/update', methods=['GET', 'POST'])
def update_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username

    if session["user"] != username:
        flash("You don't have permission to do that!")
        return redirect('/login')

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():

        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{username}')

    else:

        return render_template('feedback_update.html', form=form, feedback=feedback)


@app.route('/feedback/<int:feedback_id>/delete')
def delete_feedback(feedback_id):

    feedback = Feedback.query.get_or_404(feedback_id)
    username = feedback.username

    if session["user"] != username:
        flash("You don't have permission to do that!")
        return redirect('/login')

    db.session.delete(feedback)
    db.session.commit()

    return redirect(f'/users/{username}')
