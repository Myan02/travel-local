import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

# register user
@bp.route('/register', methods=('GET', 'POST'))
def register():
   if request.method == 'POST':
      # get data from forms
      email = request.form['email']
      username = request.form['username']
      password = request.form['password']
      first_name = request.form['first_name']
      last_name = request.form['last_name']
      location = request.form['location']
      
      # connect db
      db = get_db()
      error = None
      
      # check if any input is blank (except destination thats oke)
      if not email:
         error = 'Email is required.'
      elif not password:
         error = 'Password is required.'
      elif len(password) < 8 or len(password) > 20:
         error = 'Password must be 8-20 characters long.'
      elif not username:
         error = 'Username is required.'
      elif not first_name:
         error = 'first name is required'
      elif not last_name:
         error = 'last name is required'

      if error is None:
         try:
               # insert into table
               db.execute(
                  "INSERT INTO user (email, username, password, first_name, last_name, location) VALUES (?, ?, ?, ?, ?, ?)",
                  (email, username, generate_password_hash(password), first_name, last_name, location),
               )
               db.commit()
         except db.IntegrityError:
            # if username or email taken
            if error == 'Email is required':
               error = f"Email is taken, try again."
            else:
               error = f"User {username} is already registered."
         else:
               return redirect(url_for("auth.login"))

      flash(error)

   return render_template('auth/register.html')

# log user in
@bp.route('/login', methods=('GET', 'POST'))
def login():
   if request.method == 'POST':
      #get credentials
      email = request.form['email']
      password = request.form['password']
      
      db = get_db()
      error = None
      
      user = db.execute(
         'SELECT * FROM user WHERE email = ?', (email,)
      ).fetchone()

      # check for user existance
      if user is None:
         error = 'Incorrect email.'
      elif not check_password_hash(user['password'], password):
         error = 'Incorrect password.'

      # log user in, set id to session id token
      if error is None:
         session.clear()
         session['user_id'] = user['id']
         return redirect(url_for('index'))

      flash(error)

   return render_template('auth/login.html')

# if user already logged in, show profile
@bp.before_app_request
def load_logged_in_user():
   user_id = session.get('user_id')

   if user_id is None:
      g.user = None
   else:
      g.user = get_db().execute(
         'SELECT * FROM user WHERE id = ?', (user_id,)
      ).fetchone()

# clear session and log out user
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# force routes to require login
def login_required(view):
   @functools.wraps(view)
   def wrapped_view(**kwargs):
      if g.user is None:
         return redirect(url_for('auth.login'))

      return view(**kwargs)

   return wrapped_view