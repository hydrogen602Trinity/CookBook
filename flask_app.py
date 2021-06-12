from typing import Any, Callable, Dict, Optional, TypeVar, Union
from fractions import Fraction
import typing

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy



app = Flask(__name__)

SQLALCHEMY_DATABASE_URI = "sqlite:///{dbfile}".format(
    dbfile='test2.db'
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
# app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db: SQLAlchemy = SQLAlchemy(app)


T = TypeVar('T', bound=type)

def restful(cls: T) -> T:
    types: Dict[str, type] = cls.__init__.__annotations__  # type: ignore

    for name, type_ in types.items():
        if not (isinstance(type_, type) or (isinstance(type_, typing._GenericAlias) and type_.__origin__ is Union)):
            raise TypeError(f'Can\'t deal with this type: {type_}')

    print(f'/api/v1/{cls.__name__.lower()}')
    @app.route(f'/api/v1/{cls.__name__.lower()}', methods=['GET', 'POST'])
    def handler():
        if request.method == 'POST':
            data = request.get_json()
            if not isinstance(data, dict):
                raise TypeError(f'Expected dictrionary in json, instead got {data}')

            params: Dict[str, Any] = {}
            
            for name, type_ in types.items():
                if name not in data:
                    raise KeyError(name)
                if isinstance(type_, type) and not isinstance(data[name], type_):
                    raise TypeError(f'Expected {type_}, but got {type(data[name])} for field {name}')
                if isinstance(type_, typing._GenericAlias):
                    if type_.__origin__ is Union and not isinstance(data[name], type_.__args__):
                        raise TypeError(f'Expected one of {type_.__args__}, but got {type(data[name])} for field {name}')

                params[name] = data
            
            print(f'params = {params}')


            return 'done'
        else:
            return 'done'


    return cls


@restful
class Ingredient(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    unit = db.Column(db.String(50))  
    _amount_num = db.Column(db.Integer)
    _amount_denom = db.Column(db.Integer)

    # db.create_all()

    def __init__(self, name: str, unit: str, amount: Union[Fraction, int, float, str]):
        self.name = name
        self.unit = unit
        self.amount = amount  # type: ignore
        super().__init__()

    @property
    def amount(self) -> Fraction:
        return Fraction(self._amount_num, self._amount_denom)
    
    @amount.setter
    def amount(self, amount: Union[Fraction, int, float, str]) -> None:
        if not isinstance(amount, Fraction):
            amount = Fraction(amount)

        self._amount_num = amount.numerator
        self._amount_denom = amount.denominator

# c = Ingredient.__table__.columns.get('name')
# c.description
# c.type.length
# c.type.python_type


def analyze(cls: db.Model):
    for c in cls.__table__.columns:
        print(f'{c.description}: {c.type.python_type}, {c.type.length if "length" in c.type.__dict__ else None}')


def validate(cls: db.Model, data: Dict[str, Any]):
    '''
    Throws TypeError and ValueError
    '''
    for c in cls.__table__.columns:
        if c.description not in data:
            raise KeyError(f'Missing data for column "{c.description}"')
        d = data[c.description]

        # print(f'{c.description}: {c.type.python_type}, {c.type.length if "length" in c.type.__dict__ else None}')

        if not isinstance(d, c.type.python_type):
            raise TypeError(f'Expected {c.type.python_type}, but got {type(d)}')

        if 'length' in c.type.__dict__:
            try:
                if len(d) > c.type.length:
                    raise ValueError(f'Value too long: maximum length = {c.type.length}, but got {len(d)}')
            except TypeError:
                raise ValueError(f'Value\'s length could not be determined: maximum length allowed = {c.type.length}')


@app.route('/')
def hello_world():
    return render_template("main.html")