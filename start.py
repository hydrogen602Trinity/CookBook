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

def run(args, print_=True, stream=False, shell=False):
    if print_: print('$ ' + ' '.join(args))

    if stream:
        s = subprocess.Popen(args, stderr=sys.stderr, stdout=sys.stdout, shell=shell)
    else:
        s = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell)

    try:
        # while s.wait(1):
        s.wait()
    except KeyboardInterrupt:
        print('Terminating')
        s.terminate()
        s.wait()
    
    out, err = (b'streamed to stdout', b'streamed to stderr') if stream else s.communicate()
    if s.returncode != 0:
        print_err('Warn: {} returned with {}. stderr: {}'.format(" ".join(args), s.returncode, err.decode()))
        raise subprocess.CalledProcessError(s.returncode, args, err)
    
    if print_: print(out.decode())
    if print_: print_err(err.decode())
    return out.decode(), err.decode()

def is_py_3(cmd):
    try:
        out, _ = run([cmd, '--version'])
    except subprocess.CalledProcessError:
        return False
    except OSError as e:
        return False
    except Exception as e:
        if type(e).__name__ == 'FileNotFoundError':
            return False
        raise
    # print(re.findall(r'[Pp]ython 3', err), err, out)
    return len(re.findall(r'[Pp]ython 3', out)) > 0


py_cmd = ''
if is_py_3('./init/bin/python'):
    py_cmd = './init/bin/python'
if is_py_3('./init/Scripts/python.exe'):
    py_cmd = './init/Scripts/python.exe'
else:
    to_try_version = ['3.10', '3.9', '3.8', '3.7', '3.6', '3', '']
    to_try = ['python' + v for v in to_try_version]
    for cmd in to_try:
        if is_py_3(cmd):
            py_cmd = cmd
            break

if not py_cmd:
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

            s = subprocess.Popen(['npm', 'start'], stderr=sys.stderr, stdout=sys.stdout, shell=True)
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
            out, err = run([py_cmd, '-m', 'venv', 'init'], stream=True)
    except subprocess.CalledProcessError:
        r = input('Continue without a virtual environment? (y|n)').lower()
        if r == 'n':
            raise
        elif r == 'y':
            pass
        else:
            raise ValueError('Unknown value: "{}", expected y or n'.format(r))

    out, err = run([py_cmd, '-m', 'pip', 'install', '-r', 'requirements.txt'], stream=True)

    if not exists('start.json'):
        run(['cp', 'start.example.json', 'start.json'])
    
    os.chdir('frontend')
    try:
        print('Now in {}'.format(os.path.abspath('.')))

        run(['npm', 'install'], stream=True, shell=True)
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
