from typing import Callable, TypeVar
from flask_login import current_user
from functools import wraps


F = TypeVar('F', bound=Callable)


def require_auth(f: F) -> F:
    '''
    Requires user to be logged in
    '''

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            # User not allowed here
            return '', 401

    return wrapper


def require_admin(f: F) -> F:
    '''
    Requires user to be admin
    '''

    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
            return f(*args, **kwargs)
        else:
            # User not allowed here
            return '', 401

    return wrapper
