# -*- coding: utf8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import os
import io
import re

FLAG_DOCSTRING = '"""'
FLAG_COMMENT = '#'
FLAG_FUNCTION = 'def'
FLAG_CLASS = 'class'
FLAG_EMPTY = ''
FLAG_FILE = 'file'


def process_file(file_path, output_dir, save_empty=True, package=None):
    """Sprawdza, czy podano plik pythonowy. Wywołuje parsowanie pliku i zapisuje wyniki do katalogu output_dir.

    Args:
        file_path (str): ścieżka do pliku do sparsowania
        output_dir (str): katalog na dokumentacje
        save_empty (bool): czy zapisywać puste dokumentacje (jeśli parsowanie nie zwróci żadnych linijek)
        package (str, None): pakiet, w którym znajduje się plik

    Raises:
        IOError: jeśli podany plik nie istnieje, nie jest plikiem lub nie jest plikiem pythonowym
        IOError: jeśli podany katalog nie istnieje lub nie jest katalogiem
    """

    if not _validate_python_file(file_path):
        raise IOError("ścieżka do pliku {} jest niepoprawna".format(file_path))

    if not _validate_dir(output_dir):
        raise IOError("ścieżka do katalogu {} jest niepoprawna".format(output_dir))

    file_name = os.path.split(file_path)[1][:-3]

    if package is not None:
        file_name = "{}.{}".format(package, file_name)

    docs_dict = parse_file(file_path, file_name)

    if not save_empty and len(docs_dict) == 0:
        return

    doc_lines = [' {} '.format(file_name), (len(file_name) + 2) * '+', '']

    for k in sorted(docs_dict,
                    key=lambda e: e if e.startswith('def') else ' ' + e if e.startswith('class') else '  ' + e):
        for line in docs_dict[k]:
            doc_lines.append(line)

    print('\n| *** WYNIK: ***\n|')
    print('\n'.join(map(lambda l: "| {}".format(l), doc_lines)))


def _validate_python_file(file_path):
    """Sprawdza, czy podany plik jest plikiem pythonowym.

    Args:
        file_path (str): ścieżka do pliku

    Returns:
        bool: prawda, jeśli wszystko jest ok, fałsz w przeciwnym przypadku
    """

    if not os.path.exists(file_path):
        return False

    if not os.path.isfile(file_path):
        return False

    if not file_path.endswith('.py'):
        return False

    return True


def _validate_dir(dir_path):
    """Spawdza, czy podany katalog istnieje i jest katalogiem.

    Args:
        dir_path (str): ścieżka do katalogu

    Returns:
        bool: prawda, jeśli wszystko jest ok, fałsz w przeciwnym wypadku
    """

    if not os.path.exists(dir_path):
        return False

    if not os.path.isdir(dir_path):
        return False

    return True


def parse_file(file_path, file_name):
    """Parsuje plik w poszukiwaniu docstringów. Zwraca je w postaci

    Args:
        file_path (str): ścieżka do pliku do sparsowania
        file_name (str): nazwa samego pliku, ewentualnie pakiet.plik

    Returns:
        dict: słownik, gdzie kluczem jest nazwa funkcji/klasy/moduły, a wartościami lista linijek z docstringiem
    """

    file_lines = io.open(file_path, 'r', encoding='utf8').read().splitlines()
    lines = []
    for line in file_lines:
        flag = _get_flag(line)
        spaces = _get_spaces(line)
        lines.append((spaces, flag, line))

    docs_dict = {}

    for block_name, block_docs in _process_code_block(block_lines=lines, block_type=FLAG_FILE, block_name=file_name):
        docs_dict[block_name] = block_docs

    return docs_dict


def _get_flag(line):
    """Sprawdza linijkę kodu i zwraca flagę dla niej (docstring, comment, function, class, empty)

    Args:
        line (str): linijka kodu

    Returns:
        str: flaga danej linijki kodu
    """

    sl = line.strip()

    if sl.startswith(('\'\'\'', '"""')) or sl.endswith(('\'\'\'', '"""')):
        return FLAG_DOCSTRING

    if sl.startswith('def') and sl.endswith(':'):
        return FLAG_FUNCTION

    if sl.startswith('class') and sl.endswith(':'):
        return FLAG_CLASS

    if sl.startswith('#'):
        return FLAG_COMMENT

    return FLAG_EMPTY


def _get_spaces(line):
    """Zwraca liczbę spacji we wcięciu linii.

    Args:
        line (str): linia kodu

    Returns:
        int, None: liczba spacji, None, jeśli linijka jest pusta
    """

    if not line.strip():
        return None

    return re.search(r'\S', line).start()


def _process_code_block(block_lines, block_type, block_name):
    try:
        block_spaces = block_lines[0][0]
    except IndexError:
        # plik jest pusty
        return

    print("-> przetwarzam blok kodu '{}'".format(block_name))

    if block_name.startswith('def'):
        block_name = block_name[4:]
    elif block_name.startswith('class'):
        block_name = block_name[6:]

    if block_type == FLAG_FUNCTION:
        block_name = "def {}".format(block_name)
    elif block_type == FLAG_CLASS:
        block_name = "class {}".format(block_name)

    docs_lines = []

    docstring_flags = [i for i, dl in enumerate(block_lines) if dl[0] == block_spaces and dl[1] == FLAG_DOCSTRING]
    # próbuję wybrać dwa pierwsze elementy z flagą '"""'
    # warunek jest też taki, żeby wcześniej były tylko puste linijki i komentarze jednolinijkowe
    in_docstring = lambda j: False
    if len(docstring_flags) > 1 and all(
            bl[1] == FLAG_COMMENT or bl[0] is None
            for bl in block_lines[:docstring_flags[0]]
    ):
        docs_lines.append('')
        docs_lines.append(block_name)
        docs_lines.append(len(block_name) * '=')
        docs_lines.append('')

        docs_lines.append(block_lines[docstring_flags[0]][2][block_spaces + 3:])
        for bl in block_lines[docstring_flags[0] + 1:docstring_flags[1]]:
            docs_lines.append(bl[2][block_spaces:])
        docs_lines.append(block_lines[docstring_flags[1]][2][block_spaces:-3])

        in_docstring = lambda j: docstring_flags[0] <= j <= docstring_flags[1]

    yield block_name, docs_lines

    # teraz szukam funkcji
    # żeby coś było uznane za nagłówek funkcji,
    # to musi mieć takie wcięcie jak block_spaces i nie być częścią docstringa
    functions_flags = [i for i, dl in enumerate(block_lines)
                       if dl[0] == block_spaces and dl[1] == FLAG_FUNCTION and not in_docstring(i)]

    classes_flags = [i for i, dl in enumerate(block_lines)
                     if dl[0] == block_spaces and dl[1] == FLAG_CLASS and not in_docstring(i)]

    raw_block_name = re.sub(r'\(.*\)', '', block_name)

    for cf in classes_flags:
        i = cf + 1
        while i < len(block_lines) and block_lines[i][0] != block_spaces:
            i += 1
        class_name = block_lines[cf][2].strip().replace("class", "")[:-1].strip()
        for class_name, class_docs in _process_code_block(
                block_lines=block_lines[cf + 1:i],
                block_type=FLAG_CLASS,
                block_name="{}.{}".format(raw_block_name, class_name),
        ):
            yield class_name, class_docs

    for ff in functions_flags:
        i = ff + 1
        while i < len(block_lines) and block_lines[i][0] != block_spaces:
            i += 1
        function_name = block_lines[ff][2].strip().replace("def", "")[:-1].strip()
        for func_name, func_docs in _process_code_block(
                block_lines=block_lines[ff + 1:i],
                block_type=FLAG_FUNCTION,
                block_name="{}.{}".format(raw_block_name, function_name),
        ):
            yield func_name, func_docs
