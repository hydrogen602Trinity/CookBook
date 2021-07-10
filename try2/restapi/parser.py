from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Optional, Union


@dataclass(frozen=True, init=False)
class Argument:
    '''Represents one item in json data'''
    name: str
    max_length: Optional[int]
    required: bool
    type_: Optional[type]
    default: Any
    # sub_arguments: Union[None, Argument, List[Argument]]

    def __init__(self, 
                 name: str, 
                 length: Optional[int] = None, 
                 required: bool = False,
                 type_: Optional[type] = None,
                 default: Any = None,
                #  sub_arguments: Union[None, Argument, List[Argument]] = None
                 ) -> None:
        self.name = name
        self.max_length = length
        self.required = required
        if required and default is not None:
            raise ValueError('It makes no sense to set a default if the argument is required')
        self.default = default
        self.type_ = type_
        if self.type_ is not None and self.default is not None:
            if not isinstance(self.default, self.type_):
                raise TypeError(f'default is type {type(self.default)} but required type is {self.type_}')

        # if sub_arguments is not None:
        #     if isinstance(self.type_, list) and isinstance(sub_arguments, Argument):
        #         pass
        #     elif isinstance(self.type_, dict) and isinstance(sub_arguments, list):
        #         pass
        #     else:
        #         raise ValueError(f'Sub Arguments make no sense:\nsub_arguments = {sub_arguments}\ntype_ = {self.type_}')
        # self.sub_arguments = sub_arguments

    def verify(self, obj: dict) -> Any:
        if not isinstance(obj, dict):
            raise TypeError(f'Expected dict, but got: {type(obj)}')

        if self.required and self.name not in obj:
            raise ValueError(f'Missing key "{self.name}"')

        if self.type_ and self.name in obj and not isinstance(obj[self.name], self.type_):
            raise ValueError(f'Value for key "{self.name}" is wrong type')

        value = obj.get(self.name, default=self.default)

        if self.max_length and len(value) > self.max_length:
            raise ValueError(f'Value for key "{self.name}" is too long')

        return value


class Parser:

    def __init__(self, args: List[Argument]) -> None:
        self.arguments: List[Argument] = args
        for arg in self.arguments:
            if len([e for e in self.arguments if e is not arg and e.name == arg.name]):
                raise ValueError(f'Two arguments have the same name: {arg.name}')

    def verify(self, obj: dict) -> dict:
        if not isinstance(obj, dict):
            raise TypeError(f'Expected dict, but got: {type(obj)}')

        out = {}
        for arg in self.arguments:
            out[arg.name] = arg.verify(obj)
        return out
