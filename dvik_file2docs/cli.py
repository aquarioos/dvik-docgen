# -*- coding: utf8 -*-
from __future__ import division, absolute_import, print_function, unicode_literals

import os
import argparse as ap

from . import file_to_docs as ftd


def _parse_args():
    """Parsuje parametry uruchomienia programu w wierszu poleceń.

    * paths - ścieżki do plików .py do sparsowania
    * -o/--output_dir - ścieżka do katalogu na wynik parsowania, domyślnie jest katalog aktualny katalog

    Returns:
        ap.Namespace: przestrzeń parametrów
    """

    parser = ap.ArgumentParser()

    parser.add_argument('paths', metavar='PATH', nargs='*', help="Ścieżki plików i pakietów do parsowania.")
    parser.add_argument('-o', '--output_dir', default=os.getcwd(), help="Ścieżka do katalogu na dokumentację.")
    parser.add_argument('-p', '--package', help="Pakiet.")

    return parser.parse_args()


def run():
    """Uruchamia parsowanie plików dla każdego podanego pliku w wierszu poleceń.
    """

    args = _parse_args()
    paths = [os.path.abspath(p) for p in args.paths]
    output_dir = os.path.abspath(args.output_dir)
    package = args.package

    print("-> paths = {}".format(paths))
    print("-> output_dir = {}".format(output_dir))
    print("-> package = {}".format(package))

    for f_path in paths:
        ftd.process_file(f_path, output_dir, package=package)
