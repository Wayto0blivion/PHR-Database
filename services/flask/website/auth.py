import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, session, make_response
from .models import User
from .forms import LoginForm, UserProfileForm, PasswordResetForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
import website.helper_functions as hf
from werkzeug.utils import secure_filename


auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():

    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password) and user.active_status:
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            elif not user.active_status:
                flash('Not an active user. Please contact your administrator!', category='error')
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", form=form, user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    resp = make_response(redirect(url_for('auth.login')))
    resp.set_cookie('remember_token', expires=0)
    return resp


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email is not long enough!', category='error')
        elif len(first_name) < 2:
            flash('First name is not long enough!', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def user_account():
    form = UserProfileForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password, form.current_password.data):
            user = User.query.filter_by(id=current_user.id).first()
            user.password = generate_password_hash(form.new_password.data, method='sha256')
            db.session.commit()
            session.clear()
            flash('Password changed!', category='success')
        else:
            flash('That password is incorrect!', category='error')

    return render_template('profile.html', form=form, user=current_user)

@auth.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(current_user.id)
    return render_template('profile.html', user=user)


@auth.route('/reset-user-password', methods=['GET', 'POST'])
@login_required
@hf.user_permissions("Admin")
def reset_user_password():

    form = PasswordResetForm()

    if form.validate_on_submit():
        username = form.username.data
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data

        user = User.query.filter_by(email=username).first()
        if user:
            if new_password != confirm_password:
                flash("Passwords Don\'t Match!", category='error')
            elif len(new_password) < 7:
                flash('Password Must Be At Least 7 Characters', category='error')
            else:
                user.password = generate_password_hash(new_password, method='sha256')
                db.session.commit()
        else:
            flash('Email Does Not Exist', category='error')

    return render_template('admin_password_reset.html', form=form, user=current_user)

