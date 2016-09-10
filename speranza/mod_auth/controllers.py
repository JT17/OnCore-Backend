from flask import Blueprint, flash, render_template, redirect, request, session, url_for
from werkzeug.security import check_password_hash

from speranza.mod_auth.forms import LoginForm
from speranza.mod_managers.models import Manager

mod_auth = Blueprint('auth', __name__)


# Set the route and accepted methods
@mod_auth.route('/signin/', methods=['GET', 'POST'])
def signin():
    # If sign in form is submitted
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():

        manager = Manager.query.filter_by(email=form.email.data).first()

        if manager and check_password_hash(manager.password, form.password.data):
            session['user_id'] = manager.id

            flash('Welcome %s' % manager.name)

            return redirect(url_for('auth.home'))

        flash('Wrong email or password', 'error-message')

    return render_template("mod_auth/signin.html", form=form)
