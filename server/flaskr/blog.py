from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
   db = get_db()
   posts = db.execute(
      'SELECT p.id, destination, body, created, author_id, username'
      ' FROM post p JOIN user u ON p.author_id = u.id'
      ' ORDER BY created DESC;'
   ).fetchall()
   
   return render_template('blog/index.html', posts=posts)
 
@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
   if request.method == 'POST':
      destination = request.form['destination']
      body = request.form['body']
      error = None

      if not destination:
         error = 'Destination is required.'

      if error is not None:
         flash(error)
      else:
         db = get_db()
         db.execute(
               'INSERT INTO post (destination, body, author_id)'
               ' VALUES (?, ?, ?)',
               (destination, body, g.user['id'])
         )
         db.commit()
         return redirect(url_for('blog.index'))

   return render_template('blog/create.html')
 
def get_post(id, check_author=True):
   post = get_db().execute(
      'SELECT p.id, destination, body, created, author_id, username'
      ' FROM post p JOIN user u ON p.author_id = u.id'
      ' WHERE p.id = ?',
      (id,)
   ).fetchone()

   if post is None:
      abort(404, f"Post id {id} doesn't exist.")

   if check_author and post['author_id'] != g.user['id']:
      abort(403)

   return post
 
@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
   post = get_post(id)

   if request.method == 'POST':
      destination = request.form['destination']
      body = request.form['body']
      error = None

      if not destination:
         error = 'Destination is required.'

      if error is not None:
         flash(error)
      else:
         db = get_db()
         db.execute(
               'UPDATE post SET destination = ?, body = ?'
               ' WHERE id = ?',
               (destination, body, id)
         )
         db.commit()
         
         return redirect(url_for('blog.index'))

   return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST', ))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
 
@bp.route('/<int:id>/archive', methods=['POST'])
def archive(id):
    archive_exists = check_post(id, g.user['id'])
    db = get_db()

    if not archive_exists:
        db.execute('INSERT INTO archive (user_id, post_id)'
                   ' VALUES (?, ?)', 
                   (g.user['id'], id))
    else:
        db.execute('DELETE FROM archive WHERE post_id = ? AND user_id = ?', (id, g.user['id']))

    db.commit()
    return jsonify(success=True)

# Add a new route for the profile page to handle immediate deletion
@bp.route('/archive', methods=['POST'])
def archive_profile():
    post_id = request.form.get('id')
    if post_id is None:
        return jsonify(success=False, error="Post ID is missing")

    archive_exists = check_post(post_id, g.user['id'])
    db = get_db()

    if archive_exists:
        db.execute('DELETE FROM archive WHERE post_id = ? AND user_id = ?', (post_id, g.user['id']))
        db.commit()

        return jsonify(success=True)
    else:
        return jsonify(success=False, error="Post not found in archive")

def check_post(id, user_id):
   archive_exists = get_db().execute(
      'SELECT *'
      ' FROM archive'
      ' WHERE post_id = ? AND user_id = ?',
      (id, user_id)
   ).fetchone()

   return archive_exists is not None
   
   
   