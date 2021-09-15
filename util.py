from os import getenv as os_getenv
from typing import Any


def getenv(name: str) -> str:
    '''
    Gets an env variables and throws
    an AssertianError if not found or empty
    '''
    value = os_getenv(name)
    assert value, f'Could not find env variabled "{name}"'
    return value
