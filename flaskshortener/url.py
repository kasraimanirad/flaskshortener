from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskshortener.auth import login_required
from flaskshortener.db import get_db
from flaskshortener.hasher import get_hasher

bp = Blueprint("url", __name__)

@bp.route("/", methods=('GET', 'POST'))
@login_required
def index():
    """Show all the posts, most recent first."""
    db = get_db()
#     posts = db.execute(
#         "SELECT p.id, title, body, created, author_id, username"
#         " FROM post p JOIN user u ON p.author_id = u.id"
#         " ORDER BY created DESC"
#     ).fetchall()
#     return render_template("blog/index.html", posts=posts)
#
#   conn = get_db_connection()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('url.index'))

        url_data = db.execute('INSERT INTO urls (original_url) VALUES (?)',
                                (url,))
        db.commit()
        #db.close()

        url_id = url_data.lastrowid
        hashid = get_hasher().encode(url_id)
        short_url = request.host_url + hashid

        return render_template('url/index.html', short_url=short_url)

    return render_template('url/index.html')

# def get_post(id, check_author=True):
#     """Get a post and its author by id.
#
#     Checks that the id exists and optionally that the current user is
#     the author.
#
#     :param id: id of post to get
#     :param check_author: require the current user to be the author
#     :return: the post with author information
#     :raise 404: if a post with the given id doesn't exist
#     :raise 403: if the current user isn't the author
#     """
#     post = (
#         get_db()
#         .execute(
#             "SELECT p.id, title, body, created, author_id, username"
#             " FROM post p JOIN user u ON p.author_id = u.id"
#             " WHERE p.id = ?",
#             (id,),
#         )
#         .fetchone()
#     )
#
#     if post is None:
#         abort(404, f"Post id {id} doesn't exist.")
#
#     if check_author and post["author_id"] != g.user["id"]:
#         abort(403)
#
#     return post


# @bp.route("/create", methods=("GET", "POST"))
# @login_required
# def create():
#     """Create a new post for the current user."""
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None
#
#         if not title:
#             error = "Title is required."
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 "INSERT INTO post (title, body, author_id) VALUES (?, ?, ?)",
#                 (title, body, g.user["id"]),
#             )
#             db.commit()
#             return redirect(url_for("blog.index"))
#
#     return render_template("blog/create.html")


@bp.route("/<id>")
def url_redirect(id):
    db = get_db()

    original_id = get_hasher().decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = db.execute('SELECT original_url, clicks FROM urls'
                                ' WHERE id = (?)', (original_id,)
                                ).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        db.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                     (clicks+1, original_id))

        db.commit()
        #conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('url.index'))

# def update(id):
#     """Update a post if the current user is the author."""
#     post = get_post(id)
#
#     if request.method == "POST":
#         title = request.form["title"]
#         body = request.form["body"]
#         error = None
#
#         if not title:
#             error = "Title is required."
#
#         if error is not None:
#             flash(error)
#         else:
#             db = get_db()
#             db.execute(
#                 "UPDATE post SET title = ?, body = ? WHERE id = ?", (title, body, id)
#             )
#             db.commit()
#             return redirect(url_for("blog.index"))
#
#     return render_template("blog/update.html", post=post)

@bp.route('/stats')
@login_required
def stats():
    db = get_db()
    db_urls = db.execute('SELECT id, created, original_url, clicks FROM urls'
                           ).fetchall()
    # conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + get_hasher().encode(url['id'])
        urls.append(url)

    return render_template('url/stats.html', urls=urls)
# @bp.route("/<int:id>/delete", methods=("POST",))
# @login_required
# def delete(id):
#     """Delete a post.
#
#     Ensures that the post exists and that the logged in user is the
#     author of the post.
#     """
#     get_post(id)
#     db = get_db()
#     db.execute("DELETE FROM post WHERE id = ?", (id,))
#     db.commit()
#     return redirect(url_for("blog.index"))
