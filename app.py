from flask import Flask, render_template, redirect, session
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.exceptions import Unauthorized

from models import db, connect_db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm, DeleteForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)

connect_db(app)

with app.app_context():
    db.create_all()


@app.route('/')
def homepage():
    '''homepage, redirect to register'''
    return redirect('/register')


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''for user registration'''
    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data

        user = User.register(username, password, first_name, last_name, email)

        db.session.commit()
        session['username'] = user.username

        return redirect(f'/users/{user.username}')

    else:
        return render_template('users/register.html', form = form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    '''handle user login'''
    if 'username' in session:
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
            return render_template('users/login.html', form = form)

    return render_template('users/login.html', form = form)


@app.route('/logout')
def logout():
    '''logout'''
    session.pop('username')
    return redirect('/login')


@app.route('/users/<username>')
def show_user(username):
    '''logged-in user information page'''
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    form = DeleteForm()

    return render_template('users/info.html', user=user, form=form)


@app.route('/users/<username>/delete', methods=['POST'])
def remove_user(username):
    '''remove user and redirect to login'''
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')

    return redirect('/login')


@app.route('/users/<username>/feedback/new', methods=['GET', 'POST'])
def new_feedback(username):
    '''add new feedback'''
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title = title, content = content, username = username)

        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{feedback.username}")

    else:
        return render_template("feedback/new.html", form = form)


@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def update_feedback(id):
    '''update the feedback'''
    feedback = Feedback.query.get(id)

    if 'username' not in session or feedback.username != session['username']:
        raise   Unauthorized()

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()
        return redirect(f"/users/{feedback.username}")

    return render_template('/feedback/edit.html', form=form, feedback=feedback)


@app.route('/feedback/<int:id>/delete', methods=['POST'])
def delete_feedback(id):
    '''delete feedback'''
    feedback = Feedback.query.get(id)
    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()

    return redirect(f"/users/{feedback.username}")