# -*- coding: utf8 -*-
from __future__ import division, absolute_import, print_function

import argparse as ap
import os
import re
import io


def run():
    print('hello')

    args = _parse_args()

    paths = [os.path.abspath(p) for p in args.paths]

    print(paths)

    for p in paths:
        _process_path(p)


def _parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument('paths', metavar='PATH', nargs='*', help="Ścieżki plików i pakietów do parsowania.")
    return parser.parse_args()


def _process_path(path):
    if os.path.isdir(path) and "__init__.py" in os.listdir(path):
        _process_package(path)
    elif path.endswith(".py") and os.path.exists(path):
        _process_file(path)


def _process_package(path):
    """Wybiera pliki pythonowe w pakiecie. Wywołuje _process_file() dla każdego z nich.

    Args:
        path: ścieżka do pliku
    """

    print('_process_package')

    module = os.path.split(path)[1]

    for fname, fpath in map(lambda fname: (fname, os.path.join(path, fname)), os.listdir(path)):
        if not fname.endswith('.py'):
            continue
        print(fname, fpath)
        _process_file(fpath, module)


def _process_file(path, module=None):
    """Parsuje plik pythonowy w poszukiwaniu docstringów.

    Args:
        path (str): ścieżka do pliku
        module (str, None): moduł, do którego należy plik, jeśli None, to znaczy, że nie należy do żadnego
    """

    print('_process_file {} from {}'.format(path, module))

    lines = io.open(path, 'r', encoding='utf8').read().splitlines()
    file_docstring = []  # tutaj wrzucać CAŁE linijki!
    file_docstring_start, file_docstring_end = None, None
    data_lines = []
    for i, l in enumerate(lines):
        sl = l.strip()
        if not sl:
            data_lines.append((None, '', l))
            continue

        spaces = re.search(r'\S', l).start()
        flag = ''
        if sl.startswith(('\'\'\'', '"""')) or sl.endswith(('\'\'\'', '"""')):
            flag = '"""'
            # if file_docstring_start is None:
            #     file_docstring_start = i
            # elif file_docstring_end is None:
            #     file_docstring_end = i + 1
        elif sl.startswith('def'):
            flag = 'def'
        elif sl.startswith('class'):
            flag = 'class'
        else:
            flag = ''
        data_lines.append((spaces, flag, l))

    docstring_flags = [i for i, dl in enumerate(data_lines) if dl[1] == '"""']
    print('\tdocstring_flags:', docstring_flags)

    if len(docstring_flags) > 1:
        print('\n--- docstring --- {} ---'.format(path))
        for dl in data_lines[docstring_flags[0]:docstring_flags[1] + 1]:
            print(dl[2])
        print('-----------------\n')
    else:
        print('w pliku {} nie ma docstringa...'.format(path))


def _process_function(source, module):
    """Parsuje funkcję w poszukiwaniu docstringów, funkcji i klas.

    Args:
        source (list): kod funkcji w postaci listy linijek
        module (str): jest to moduł zawierający daną funkcję/metodę
    """

    print('_process_function')


def _process_class(source, module):
    """Parsuje klasę w poszukiwaniu docstringów i metod.

    Args:
        source (list): kod funkcji w postaci listy linijek
        module (str): jest to moduł zawierający daną klasę
    """

    print('_process_class')
