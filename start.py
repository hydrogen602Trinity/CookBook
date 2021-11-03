#!/usr/bin/env python
from __future__ import print_function
import sys
import os
import re
import json
import subprocess
from os.path import exists

# The startup script is compatible with python2 and python3, it will look for python3 itself


# needs to be customized in start.json
p = 'start.json'
if exists(p):
    with open(p) as f:
        obj = json.load(f)
else:
    print('Warn: Falling back to default as start.json could not be found')
    with open('start.example.json') as f:
        obj = json.load(f)

startDB = obj['startDB']
stopDB = obj['stopDB']


def print_usage():
    print('Usage: {} install|test|init|run|run-front'.format(sys.argv[0]))
    print('Usage: {} pg start|stop'.format(sys.argv[0]))


if len(sys.argv) < 2:
    print_usage()
    exit(1)


def print(*args, **kwargs):
    if sum(map(lambda x: len(str(x)), args)) > 0:
        __builtins__.print(*args, **kwargs)

def print_err(*args, **kwargs):
    kwargs['file'] = sys.stderr
    print(*args, **kwargs)

def run(args, print_=True):
    if print_: print('$ ' + ' '.join(args))
    s = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        s.wait()
    except KeyboardInterrupt:
        s.terminate()
        s.wait()
    out, err = s.communicate()
    if s.returncode != 0:
        print_err('Warn: {} returned with {}. stderr: {}'.format(" ".join(args), s.returncode, err.decode()))
        raise subprocess.CalledProcessError(s.returncode, args, err)
    
    if print_: print(out.decode())
    if print_: print_err(err.decode())
    return out.decode(), err.decode()

def is_py_3(cmd):
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

print('Using command: {}'.format(py_cmd))


os.environ['FLASK_APP'] = 'flask_app.py'
os.environ['FLASK_ENV'] = 'development'
os.environ['INIT_DB'] = '0'


def main(front=False):
    if front:
        os.chdir('frontend')
        try:
            print('Now in {}'.format(os.path.abspath('.')))

            s = subprocess.Popen(['npm', 'start'], stderr=sys.stderr, stdout=sys.stdout)
            try:
                s.wait()
            except KeyboardInterrupt:
                s.terminate()
                s.wait()
        finally:
            os.chdir('..')
            print('Now in {}'.format(os.path.abspath('.')))

    else:
        os.environ['DB_FILENAME'] = 'recipedb'
        s = subprocess.Popen([py_cmd, '-m', 'flask', 'run', '--host=0.0.0.0'], stderr=sys.stderr, stdout=sys.stdout, bufsize=0)
        s.wait()

if sys.argv[1] == 'install':
    try:
        if not exists('init'):
            out, err = run([py_cmd, '-m', 'venv', 'init'])
    except subprocess.CalledProcessError:
        r = input('Continue without a virtual environment? (y|n)').lower()
        if r == 'n':
            raise
        elif r == 'y':
            pass
        else:
            raise ValueError('Unknown value: "{}", expected y or n'.format(r))

    out, err = run([py_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'])

    if not exists('start.json'):
        run(['cp', 'start.example.json', 'start.json'])
    
    os.chdir('frontend')
    try:
        print('Now in {}'.format(os.path.abspath('.')))

        run(['npm', 'install'])
    finally:
        os.chdir('..')
        print('Now in {}'.format(os.path.abspath('.')))


elif sys.argv[1] == 'test':
    os.environ['INIT_DB'] = '0'
    os.environ['DB_FILENAME'] = 'postgres'
    os.environ['TESTING'] = '1'

    out, err = run([py_cmd, '-m', 'unittest', '--locals'])

    os.chdir('frontend')
    try:
        print('Now in {}'.format(os.path.abspath('.')))

        os.environ['CI'] = 'true'
        run(['npm', 'test'])
    finally:
        os.chdir('..')
        print('Now in {}'.format(os.path.abspath('.')))

elif sys.argv[1] == 'init':
    os.environ['INIT_DB'] = '1'
    main()

elif sys.argv[1] == 'run':
    main()

elif sys.argv[1] == 'run-front':
    main(front=True)

elif sys.argv[1] == 'pg':
    if len(sys.argv) < 3:
        print_usage()
    if sys.argv[2] == 'start':
        run(startDB)
    elif sys.argv[2] == 'stop':
        run(stopDB)
    else:
        print_usage()

else:
    print_usage()
    exit(1)
