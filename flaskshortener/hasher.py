from hashids import Hashids
from flask import current_app
from flask import g

def get_hasher():
    if "hashids" not in g:
        g.hashids = Hashids(min_length=6, salt=current_app.config['SECRET_KEY'])
    return g.hashids