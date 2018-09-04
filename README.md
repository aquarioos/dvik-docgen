# dvik-docgen
Generator dokumentacji. Parsuje rekurencyjnie pliki w modułach i wybiera z nich tylko docstringi.

## Wersja

0.2

## Zmiany

### 0.2

* podział na *file2docs* i *package2docs*
* implemenacja *file2docs*, przetestowane

## Instalacja

    pip install git+https://github.com/aquarioos/dvik-docgen/#egg=dvik-docgen

## file2docs

### Samodzielne uruchomienie

Po instalacji pakietu są dwie możliwości jego samodzielnego uruchomienia.

**Jako moduł języka Python:**

    python -m dvik_file2docs [parametry]

**Za pomocą punktu wejściowego (entry point):**

    dvik-file2docs [parametry]

### API

*dvik-file2docs* jest również dostępne jako biblioteka języka Python. Udostępnia dwie funkcje:

#### `process_file(file_path, output_dir, save_empty=True, package=None)`

Sprawdza, czy podano plik pythonowy. Wywołuje parsowanie pliku i zapisuje wyniki do katalogu output_dir.

**Argumenty:**

* **file_path** *(str)*: ścieżka do pliku do sparsowania
* **output_dir** *(str)*: katalog na dokumentacje
* **save_empty** *(bool)*: czy zapisywać puste dokumentacje (jeśli parsowanie nie zwróci żadnych linijek)
* **package** *(str, None)*: pakiet, w którym znajduje się plik

**Wyjątki:**

* **IOError**: jeśli podany plik nie istnieje, nie jest plikiem lub nie jest plikiem pythonowym
* **IOError**: jeśli podany katalog nie istnieje lub nie jest katalogiem

#### `parse_file(file_path, file_name)`

Parsuje plik w poszukiwaniu docstringów. Zwraca je w postaci słownika, gdzie kluczem jest nazwa bloku, a wartością lista linii dostringa.

**Argumenty:**

* **file_path** (*str*): ścieżka do pliku do sparsowania
* **file_name** (*str*): nazwa samego pliku, ewentualnie pakiet.plik

**Zwraca:**

* **dict**: słownik, gdzie kluczem jest nazwa funkcji/klasy/moduły, a wartościami lista linijek z docstringiem

## package2docs
