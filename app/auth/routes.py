"""
Authentication routes (Login, Logout, Register).
Implements FR: Auth Routes.
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from app import db
from app.models import User, Company
from app.auth import auth
from app.auth.forms import LoginForm, RegisterForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    Implements FR: User Login.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('Successfully logged in!', 'success')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)

@auth.route('/logout')
@login_required
def logout():
    """
    Handle user logout.
    Implements FR: User Logout.
    """
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    """
    Public registration endpoint.
    Disabled: All tenant accounts and initial users must be provisioned by the Platform Superadmin.
    """
    flash('Public registration is disabled. Tenant accounts are provisioned exclusively by the platform administrator.', 'warning')
    return redirect(url_for('auth.login'))

