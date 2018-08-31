# -*- coding: utf8 -*-
from __future__ import division, absolute_import, print_function

import argparse as ap
import os
import io

from . import parser


def run():
    args = _parse_args()

    paths = [os.path.abspath(p) for p in args.paths]

    for p in paths:
        print('*** {} ***'.format(p))
        _process_path(p, recursive=args.recursive, output_dir=args.output_dir, base_module=args.base_module)


def _parse_args():
    parser = ap.ArgumentParser()
    parser.add_argument('paths', metavar='PATH', nargs='*', help="Ścieżki plików i pakietów do parsowania.")
    parser.add_argument('-r', '--recursive', action='store_true')
    parser.add_argument('-o', '--output_dir', default=os.getcwd(), help="Ścieżka do katalogu na dokumentację.")
    parser.add_argument('-b', '--base_module', help="Nazwa bazowego modułu.")
    return parser.parse_args()


def _process_path(path, recursive, output_dir, base_module=None):
    """Przetwarza ścieżkę.
    Rozpoznaje, czy ścieżka jest do pakiety, czy do konkretnego pliku .py.
    Jeśli nie jest ani jednym, ani drugim, to nic się nie dzieje.

    Args:
        path: ścieżka
        recursive: czy przetwarzać moduły rekurencyjnie
        output_dir: ścieżka do katalogu na wyniki
        base_module: nazwa bazowego modułu, może być None
    """

    print(path, base_module)

    res_lines = []

    if os.path.isdir(path) and "__init__.py" in os.listdir(path):
        parser.process_package(path=path, recursive=recursive, output_dir=output_dir, module=base_module,
                               res_lines=res_lines)
    elif path.endswith(".py") and os.path.exists(path):
        parser.process_file(path=path, output_dir=output_dir, module=base_module, res_lines=res_lines)

    out_file_name = os.path.split(path)[1]
    if out_file_name.endswith('.py'):
        out_file_name = out_file_name[:-3]
    if not out_file_name.endswith('.rst'):
        out_file_name = '{}.rst'.format(out_file_name)

    out_file_path = os.path.join(output_dir, out_file_name)
    if len(res_lines) > 0:
        file_content = '\n'.join(res_lines)
        with io.open(out_file_path, 'w', encoding='utf8') as fp:
            fp.write(file_content)
        print("zapisano do pliku {}".format(out_file_path))
        return "{}.rst".format(out_file_name)
