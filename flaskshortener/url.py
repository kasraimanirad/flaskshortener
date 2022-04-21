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

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('The URL is required!')
            return redirect(url_for('url.index'))

        url_data = db.execute('INSERT INTO urls (original_url) VALUES (?)',
                                (url,))
        db.commit()


        url_id = url_data.lastrowid
        hashid = get_hasher().encode(url_id)
        short_url = request.host_url + hashid

        return render_template('url/index.html', short_url=short_url)

    return render_template('url/index.html')


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
