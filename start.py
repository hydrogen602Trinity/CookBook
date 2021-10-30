#!/usr/bin/env python3
from __future__ import print_function
import sys
import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Tuple

# needs to be customized in start.json
p = Path('start.json')
if p.exists():
    with p.open() as f:
        obj = json.load(f)
else:
    print('Warn: Falling back to default as start.json could not be found')
    with open('start.example.json') as f:
        obj = json.load(f)

startDB = obj['startDB']
stopDB = obj['stopDB']


if len(sys.argv) < 2:
    print(f'Usage: {sys.argv[0]} install|test|init|run')
    print(f'Usage: {sys.argv[0]} pg start|stop')
    exit(1)


def print(*args, **kwargs):
    if sum(map(lambda x: len(str(x)), args)) > 0:
        __builtins__.print(*args, **kwargs)

def print_err(*args, **kwargs):
    print(*args, **kwargs, file=sys.stderr)

def run(args: List[str], print_=True) -> Tuple[str, str]:
    if print_: print('$ ' + ' '.join(args))
    s = subprocess.run(args, capture_output=True)
    if s.returncode != 0:
        print_err(f'Warn: {" ".join(args)} returned with {s.returncode}. stderr: {s.stderr.decode()}')
        s.check_returncode()
    
    if print_: print(s.stdout.decode())
    if print_: print_err(s.stderr.decode())
    return s.stdout.decode(), s.stderr.decode()

def is_py_3(cmd: str) -> bool:
    try:
        out, _ = run([cmd, '--version'])
    except subprocess.CalledProcessError as e:
        return False
    # print(re.findall(r'[Pp]ython 3', err), err, out)
    return len(re.findall(r'[Pp]ython 3', out)) > 0


py_cmd = ''
if is_py_3('./init/bin/python'):
    py_cmd = './init/bin/python'
elif is_py_3('python'):
    py_cmd = 'python'
elif is_py_3('python3'):
    py_cmd = 'python3'
else:
    print('Could not find python3')
    exit(1)

print(f'Using command: {py_cmd}')


os.environ['FLASK_APP'] = 'flask_app.py'
os.environ['FLASK_ENV'] = 'development'
os.environ['INIT_DB'] = '0'


def main():
    os.environ['DB_FILENAME'] = 'prod.db'
    subprocess.run([py_cmd, '-m', 'flask', 'run', '--host=0.0.0.0'], stderr=sys.stderr, stdout=sys.stdout)


if sys.argv[1] == 'install':
    try:
        if not Path('init').exists():
            out, err = run([py_cmd, '-m', 'venv', 'init'])
    except subprocess.CalledProcessError:
        r = input('Continue without a virtual environment? (y|n)').lower()
        if r == 'n':
            raise
        elif r == 'y':
            pass
        else:
            raise ValueError(f'Unknown value: "{r}", expected y or n')

    out, err = run([py_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    if not Path('start.json').exists():
        run(['cp', 'start.example.json', 'start.json'])


elif sys.argv[1] == 'test':
    os.environ['INIT_DB'] = '0'
    os.environ['DB_FILENAME'] = 'test.db'
    os.environ['TESTING'] = '1'

    out, err = run([py_cmd, '-m', 'unittest', '--locals'])

elif sys.argv[1] == 'init':
    os.environ['INIT_DB'] = '1'
    main()

elif sys.argv[1] == 'run':
    main()

elif sys.argv[1] == 'pg':
    if len(sys.argv) < 3:
        print(f'Usage: {sys.argv[0]} pg start|stop')
    if sys.argv[2] == 'start':
        run(startDB)
    elif sys.argv[2] == 'stop':
        run(stopDB)
    else:
        print(f'Usage: {sys.argv[0]} pg start|stop')

else:
    print(f'Usage: {sys.argv[0]} install|test|init|run')
    print(f'Usage: {sys.argv[0]} pg start|stop')
    exit(1)
