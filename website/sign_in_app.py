from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for

app  = Flask(__name__)


# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SECRET_KEY'] = 'password'

# initialize the app with the extension
db = SQLAlchemy()
db.init_app(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    sign_in_time = db.Column(db.DateTime(timezone=True), nullable=True)#, server_default=func.now())
    sign_out_time = db.Column(db.DateTime(timezone=True), nullable=True)
    interval = db.Column(db.Interval, nullable=True)

    #time = db.Column(db.DateTime, default = datetime.utcnow)

    # def __repr__(self) -> str:
    #     return f"{self.sno} - {self.title}"


@app.route("/",methods=['GET','POST'])
def index():
    # if request.method == 'POST':
    #     todo_title = request.form['title']
    #     desc_todo = request.form['desc']
    #     data = Todo(title=todo_title, desc=desc_todo)
    #     db.session.add(data)
    #     db.session.commit()
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route("/login",methods=['GET','POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                #login_user(user, remember=True)
                sign_in_time = datetime.now()
                user.sign_in_time = sign_in_time
                db.session.add(user)
                db.session.commit()
                users = User.query.all()
                return render_template("index.html", users=users)
                #return redirect(url_for('index'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("sign_in.html")

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, last_name=last_name, \
                    password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
        #    login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('index'))
    return render_template("sign_up.html")













@app.route('/sign_out/<int:sno>', methods=['GET','POST'])
def update(sno):
    if request.method=='POST':
        # return "Na POST request bro!!!"
        todo_title = request.form['title']
        desc_todo = request.form['desc']
        data = Todo.query.filter_by(sno=sno).first()
        # this is prepping data that'll used to change the db
        data.title = todo_title
        data.desc = desc_todo
        # now changing the db
        db.session.add(data)
        db.session.commit
        # return redirect('/')
        alltodo = Todo.query.all()
        return render_template('index.html', alltodo=alltodo)

    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)


@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
