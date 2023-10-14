from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from .models import User #Tracker
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime


auth = Blueprint('auth', __name__)

def newest_day():
    '''A function that returns the latest sign_in date if there have been sign_ins over
       a couple of days or None if the curent sign in is the first.'''

    users = User.query.all()

    # aggregating the sign_in dates
    sign_in_dates = []

    if users:
        for user in users:
            date = user.sign_in_time.date()
            sign_in_dates.append(date)

        # arbitrarily assigning the first date to newest_day
        latest_date = sign_in_dates[0]

        for date in sign_in_dates:
            if date > latest_date:
                latest_date = date

        return latest_date

    else:
        return None

@auth.route('/login', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                sign_in_time = datetime.now()
                user.sign_in_time = sign_in_time
                user.sign_in_status = True
                db.session.add(user)
                db.session.commit()
                # user = User.query.filter_by(email=email).first()
                user = User.query.all()

                new_date = newest_day()
                if new_date != None:
                    return render_template('report.html', user=user, new_date=new_date)

            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("sign_in.html", user=current_user)


@auth.route('/sign_out/<int:id>', methods=['GET', 'POST'])
@login_required
def sign_out(id):
    if request.method == 'GET':
        sign_out_time = datetime.now()
        user = User.query.filter_by(id=id).first()
        user.sign_out_time = sign_out_time
        user.sign_in_status = False
        user.interval = (user.sign_out_time) - (user.sign_in_time)
        db.session.add(user)
        db.session.commit()
        user = User.query.all()

        new_date = newest_day()
        if new_date != None:
            return render_template('report.html', user=user, new_date=new_date)

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        last_name = request.form.get('lastName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists. Please use another one.', category='error')
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
            #login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('auth.sign_in'))
    return render_template("sign_up.html")
