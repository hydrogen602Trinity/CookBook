from __future__ import annotations
from os import getenv as os_getenv
from typing import Callable, TypeVar

ReturnType = TypeVar("ReturnType")


def getenv(name: str) -> str:
    '''
    Gets an env variables and throws
    an AssertianError if not found or empty
    '''
    value = os_getenv(name)
    assert value, f'Could not find env variabled "{name}"'
    return value


# from https://github.com/sagnibak/func_py/blob/master/curry.py
def curry(num_args: int):
    """Curries the decorated function. Instead of having to provide all arguments
    at once, they can be provided one or a few at a time. Once at least `num_args`
    arguments are provided, the wrapped function will be called. The doctests below
    best illustrate its use.
    
    Parameters
    ----------
    num_args    number of arguments to wait for before evaluating wrapped function
    Returns
    -------
    a decorator that curries a function
    """

    def decorator(fn: Callable[..., ReturnType]):
        def init(*args, **kwargs):
            def call(*more_args, **more_kwargs):
                all_args = args + more_args
                all_kwargs = dict(**kwargs, **more_kwargs)
                if len(all_args) + len(all_kwargs) >= num_args:
                    return fn(*all_args, **all_kwargs)
                else:
                    return init(*all_args, **all_kwargs)

            return call
        return init()
    return decorator
