
from functools import wraps
from typing import Any, List, Union
from flask import abort


def optional_param_check(should_exist: bool, arg_list: Union[str, List[str]]):
    '''
    A decorator that can be used to check kwargs being passed in.
    If should_exist is True, an abort is called if a value is missing.
    If should_exist is False, an abort is called if a value is present.
    '''
    if isinstance(arg_list, str):
        arg_list = (arg_list,)
    def decorator(func):
        @wraps(func)
        def wrapper(self, **kwargs):
            for arg in arg_list:
                v = kwargs.get(arg)
                if (should_exist and v is None) or (not should_exist and v is not None):
                    abort(400, {
                        'error': f'The url paramter "{arg}" should { "" if should_exist else "not " }exist in url'})
            return func(self, **kwargs)
        return wrapper
    return decorator


def handle_nonexistance(value: Any):
    '''
    Used for checking if what the database returned is None
    and send an error message if that is the case
    '''
    if value is None:
        abort(404, {'error': 'entry not found in database'})


def require_truthy_values(data: dict) -> dict:
    '''
    Used to over the result of `reqparse.RequestParser().parse_args()`
    to verify that all the values in the data are truthy
    '''
    for k, v in data.items():
        if not v:
            abort(400, {'error': f'field "{k}" missing or empty in data'})
    return data
