from flask import g,redirect,url_for
from functools import wraps


def admin_login_required(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        if hasattr(g,'userAdmin'):
            return func(*args,**kwargs)
        else:
            return redirect(url_for('admin.login'))
    return wrapper