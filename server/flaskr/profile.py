from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.auth import login_required
from flaskr.db import get_db
from flaskr.blog import index

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/')
@login_required
def profile():
   posts = get_user_posts()
   
   return render_template('profile/profile.html', posts=posts)

def get_user_posts():
   db = get_db()
   all_posts = db.execute(
      'SELECT p.*, u.username'
      ' FROM post p'
      ' JOIN archive a ON p.id = a.post_id'
      ' JOIN user u ON p.author_id = u.id'
     f' WHERE a.user_id = {session["user_id"]}'
      ' ORDER BY created DESC;'
   ).fetchall()
   
   return all_posts

