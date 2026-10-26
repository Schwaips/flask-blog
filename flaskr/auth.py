import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_session
from flaskr.models import User

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
      username = request.form['username']
      password = request.form['password']
      error = None

      if not username:
          error = 'Username is required.'
      elif not password:
          error = 'Password is required.'

      if error is None:
        db_session = get_session()
        try:
          user = User(
              username=username,
              password=generate_password_hash(password),
          )
          db_session.add(user)
          db_session.commit()
        except IntegrityError:
            db_session.rollback()
            error = f"User {username} is already registered."
        else:
            return redirect(url_for("auth.login"))

      flash(error)

  return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None
        query = select(User).where(User.username == username)

        user = get_session().scalars(query).first()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
      g.user = None
    else:
      g.user = get_session().get(User, user_id)

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
