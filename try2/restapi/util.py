from __future__ import annotations
from functools import wraps
from typing import Any, Callable, Dict, List, Union, TYPE_CHECKING
from flask import abort


if TYPE_CHECKING:
    from flask_restful import Api


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


def require_truthy_values(data: dict, exceptions: List[str] = []) -> dict:
    '''
    Used to go over the result of `reqparse.RequestParser().parse_args()`
    to verify that all the values in the data are truthy
    '''
    for k, v in data.items():
        if not v and k not in exceptions:
            abort(400, {'error': f'field "{k}" missing or empty in data'})
    return data


def require_keys_with_set_types(requirement: Dict[str, type], data: dict) -> dict:
    '''
    Used to check that certain keys exist and are of a given type
    '''
    for name, type_ in requirement.items():
        if not data.get(name) or not isinstance(data[name], type_):
            abort(400, {'error': f'field "{name}" missing, empty, or wrong type'})
    return data


def add_resource(api: Api, *paths: str) -> Callable[[type], type]:
    def decorator(cls: type) -> type:
        api.add_resource(cls, *paths)
        return cls
    return decorator
