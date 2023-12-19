from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

@bp.route('/')
def index():
   if g.user:
      db = get_db()
      posts = db.execute(
         'SELECT p.id, destination, body, created, author_id, username '
         'FROM post p JOIN user u ON p.author_id = u.id '
         'WHERE p.author_id = ? OR p.author_id IN '
         '(SELECT following_id FROM followers WHERE follower_id = ?) '
         'ORDER BY created DESC',
         (g.user['id'], g.user['id'])
      ).fetchall()

      comments = {}
      for post in posts:
         post_id = post['id']
         post_comments = db.execute(
            'SELECT c.id, body, username, created, author_id ' 
            'FROM comment c JOIN user u ON c.author_id = u.id '
            'WHERE c.post_id = ?',
            (post_id,)
         ).fetchall()
         comments[post_id] = post_comments
   
   else:
      flash("Please log in!")
      return redirect(url_for('auth.login'))
   
   return render_template('blog/index.html', posts=posts, comments=comments)
 
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
 
@bp.route('/create-comment/<int:post_id>', methods=['GET','POST'])
@login_required
def create_comment(post_id):
   text = request.form.get('text')

   if not text:
      flash("comment empty")
      return redirect(url_for('blog.index'))

   else:
      post = get_db().execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()

      if post:
         db = get_db()
         db.execute('INSERT INTO comment (body, author_id, post_id)'
                                    ' VALUES (?, ?, ?)',
               (text, g.user['id'], post_id))
         db.commit()
      else:
         flash("post does not exist")

   return redirect(url_for('blog.index')) 
 
@bp.route('/delete-comment/<int:comment_id>', methods=['GET','POST'])
@login_required
def delete_comment(comment_id):
   db = get_db()
   comment = db.execute('SELECT id, author_id, post_id FROM comment WHERE id = ?', (comment_id,)).fetchone()

   if comment is None:
      return redirect(url_for('blog.index'))

   if g.user['id'] != comment['author_id']:
        abort(403)

   db.execute('DELETE FROM comment WHERE id = ?', (comment_id,))
   db.commit()
   flash("comment deleted!")
   
   return redirect(url_for('blog.index'))

@bp.route('/user/<username>', methods = ['GET','POST'])
def user(username):
   db = get_db()
   user = db.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()

   if user is None:
      flash("username not found")

   posts = db.execute('SELECT p.id, destination, body, created, author_id, username'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE u.id = ?'
        ' ORDER BY created DESC',
        (user['id'],)
    ).fetchall() 
   
   comments = {}
   for post in posts:
      post_id = post['id']
      post_comments = db.execute(
         'SELECT c.id, body, username, created, author_id ' 
          'FROM comment c JOIN user u ON c.author_id = u.id '
          'WHERE c.post_id = ?',
          (post_id,)
      ).fetchall()
      comments[post_id] = post_comments

   follower_count = db.execute('SELECT COUNT(*) FROM followers WHERE following_id = ?', (user['id'],)).fetchone()[0]
   
   following_count = db.execute('SELECT COUNT(*) FROM followers WHERE follower_id = ?', (user['id'],)).fetchone()[0]

   return render_template('blog/user.html', posts=posts, comments=comments, user=user, follower_count=follower_count, following_count = following_count)


@bp.route('/follow/<username>', methods = ['GET','POST'])
@login_required
def follow(username):
   db = get_db()
   follow_user = db.execute('SELECT id, username FROM user WHERE username = ?', (username,)).fetchone()

   already_follow = db.execute('SELECT * FROM followers WHERE follower_id = ? AND following_id = ?', (g.user['id'], follow_user['id'])).fetchone()

   if follow_user['id'] == g.user['id']:
      flash("cannot follow self!")
   
   elif already_follow:
      flash(f"You already follow {follow_user['username']}!")
   
   else:
      db = get_db()
      db.execute('INSERT INTO followers (follower_id, following_id)'
                                    ' VALUES (?, ?)',
               (g.user['id'], follow_user['id']))
      db.commit()
      flash(f"You are now following {follow_user['username']}!")
   
   return redirect(url_for('blog.user', username=username))


@bp.route('/unfollow/<username>', methods = ['GET','POST'])
@login_required
def unfollow(username):
   db = get_db()
   unfollow_user = db.execute('SELECT id, username FROM user WHERE username = ?', (username,)).fetchone()

   already_unfollow = db.execute(
    'SELECT * FROM followers WHERE follower_id = ? AND following_id = ?', (g.user['id'], unfollow_user['id'])).fetchone()

   if unfollow_user['id'] == g.user['id']:
      flash("cannot unfollow yourself!")

   elif not already_unfollow:
      flash(f"You already unfollowed {unfollow_user['username']}!")

   else:
      db = get_db()
      db.execute('DELETE FROM followers WHERE follower_id = ? AND following_id = ?',
               (g.user['id'], unfollow_user['id']))
      db.commit()
   
   return redirect(url_for('blog.user', username=username))

 
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
   
   
   