# -*- coding: utf8 -*-
from __future__ import division, absolute_import, print_function

import argparse as ap
import os
import re
import io


def run():
    args = _parse_args()

    paths = [os.path.abspath(p) for p in args.paths]

    for p in paths:
        print('*** {} ***'.format(p))
        _process_path(p, recursive=args.recursive, output_dir=args.output_dir)


def _parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument('paths', metavar='PATH', nargs='*', help="Ścieżki plików i pakietów do parsowania.")
    parser.add_argument('-r', '--recursive', action='store_true')
    parser.add_argument('-o', '--output_dir', default=os.getcwd(), help="Ścieżka do katalogu na dokumentację.")
    return parser.parse_args()


def _process_path(path, recursive, output_dir):
    """Przetwarza ścieżkę.
    Rozpoznaje, czy ścieżka jest do pakiety, czy do konkretnego pliku .py.
    Jeśli nie jest ani jednym, ani drugim, to nic się nie dzieje.

    Args:
        path: ścieżka
        recursive: czy przetwarzać moduły rekurencyjnie
    """

    if os.path.isdir(path) and "__init__.py" in os.listdir(path):
        _process_package(path, recursive)
    elif path.endswith(".py") and os.path.exists(path):
        _process_file(path)


def _process_package(path, recursive, module=None):
    """Wybiera pliki pythonowe w pakiecie. Wywołuje _process_file() dla każdego z nich.

    Args:
        path: ścieżka do pliku
        recursive (bool): czy przetwarzać pakiety rekurencyjnie
        module: moduł
    """

    module = os.path.split(path)[1]

    for fname, fpath in map(lambda fname: (fname, os.path.join(path, fname)), os.listdir(path)):
        if os.path.isdir(fpath) and '__init__.py' in os.listdir(fpath) and recursive:
            _process_package(fpath, recursive, module)
        if not fname.endswith('.py'):
            continue
        _process_file(fpath, module)


def _process_file(path, module=None):
    """Parsuje plik pythonowy w poszukiwaniu docstringów.

    Args:
        path (str): ścieżka do pliku
        module (str, None): moduł, do którego należy plik, jeśli None, to znaczy, że nie należy do żadnego
    """

    lines = io.open(path, 'r', encoding='utf8').read().splitlines()
    file_lines = []
    for i, l in enumerate(lines):
        flag = ''

        sl = l.strip()
        if not sl:
            file_lines.append((None, flag, l))
            continue

        spaces = re.search(r'\S', l).start()
        if sl.startswith(('\'\'\'', '"""')) or sl.endswith(('\'\'\'', '"""')):
            flag = '"""'
        elif sl.startswith('def') and sl.endswith(':'):
            flag = 'def'
        elif sl.startswith('class') and sl.endswith(':'):
            flag = 'class'
        elif sl.startswith('#'):
            flag = '#'

        file_lines.append((spaces, flag, l))

    _process_code_block(
        block_lines=file_lines,
        block_type='file',
        header=os.path.split(path)[1],
        module=module,
    )


def _process_code_block(block_lines, block_type, res_lines, header=None, module=None):
    """Przetarza blok kodu. Blokiem kodu nazywamy:

    * zawartość pliku (header=nazwa pliku, module=nazwa modułu albo nic)
    * zawartość funkcji (header=nazwa funkcji bez ':', module=moduł, z którego było wywołane np. plik, klasa, inna funkcja)
    * zawartość klasy (header=nazwa klasy bez ':', module=moduł - rodzic

    Args:
        block_lines (list): linijki z kodem [(spaces, flag, line), ...]
        block_type: rodzaj: file, class, def
        res_lines: lista z liniami dokumentacji
        header: nazwa pliku/funkcji/klasy
        module: nazwa modułu-rodzica
    """

    try:
        block_spaces = block_lines[0][0]
    except IndexError:
        # plik jest pusty
        return

    curr_module = None
    if module is None:
        if block_type == 'file':
            curr_module = header[:-3]
        elif block_type == 'def':
            curr_module = header[4:]
        elif block_type == 'class':
            curr_module = header[6:]
    else:
        if block_type == 'file':
            curr_module = "{}.{}".format(module, header[:-3])
        elif block_type == 'def':
            curr_module = "{}.{}".format(module, header[4:])
        elif block_type == 'class':
            curr_module = "{}.{}".format(module, header[6:])

    if curr_module is None:
        raise ValueError('curr_module jest None')

    if curr_module.endswith(')'):
        i = len(curr_module) - 1
        while curr_module[i] != '(':
            i -= 1
        curr_module = curr_module[:i]

    docstring_flags = [i for i, dl in enumerate(block_lines) if dl[0] == block_spaces and dl[1] == '"""']
    # próbuję wybrać dwa pierwsze elementy z flagą '"""'
    # warunek jest też taki, żeby wcześniej były tylko puste linijki i komentarze jednolinijkowe
    in_docstring = lambda i: False
    if len(docstring_flags) > 1 and all(bl[1] == '#' or bl[0] is None for bl in block_lines[:docstring_flags[0]]):
        header_name = header[4:] if header.startswith('def') else header[6:]
        if block_type == 'def':
            header_name = header[4:]
        elif block_type == 'class':
            header_name = header[6:]
        else:
            header_name = header

        if module is not None:
            print('\n*** {} {}.{}'.format(block_type, module, header_name))
        else:
            print('\n*** {} {}'.format(block_type, header_name))

        print('""|', block_lines[docstring_flags[0]][2][block_spaces + 3:])
        for bl in block_lines[docstring_flags[0] + 1:docstring_flags[1]]:
            print('""|', bl[2][block_spaces:])
        print('""|', block_lines[docstring_flags[1]][2][block_spaces:-3])
        in_docstring = lambda i: docstring_flags[0] <= i <= docstring_flags[1]

    # teraz szukam funkcji
    # żeby coś było uznane za nagłówek funkcji,
    # to musi mieć takie wcięcie jak block_spaces i nie być częścią docstringa
    functions_flags = [i for i, dl in enumerate(block_lines)
                       if dl[0] == block_spaces and dl[1] == 'def' and not in_docstring(i)]

    classes_flags = [i for i, dl in enumerate(block_lines)
                     if dl[0] == block_spaces and dl[1] == 'class' and not in_docstring(i)]

    for ff in functions_flags:
        i = ff + 1
        while i < len(block_lines) and block_lines[i][0] != block_spaces:
            i += 1
        _process_code_block(
            block_lines=block_lines[ff + 1:i],
            block_type='def',
            header=block_lines[ff][2].strip()[:-1],
            module=curr_module
        )

    for cf in classes_flags:
        i = cf + 1
        while i < len(block_lines) and block_lines[i][0] != block_spaces:
            i += 1
        _process_code_block(
            block_lines=block_lines[cf + 1:i],
            block_type='class',
            header=block_lines[cf][2].strip()[:-1],
            module=curr_module
        )
