#!/usr/bin/env python3
# coding: utf-8
#!/usr/bin/env python3
# coding: utf-8
import os
import sys


def add_sigla(directory, filter_string, sigla):
    # Ottieni la directory specificata
    target_directory = directory

    # Elenca tutti i file nella directory specificata
    files = os.listdir(target_directory)

    # Filtra i file che contengono la stringa di filtro
    filtered_files = [file for file in files if filter_string in file]

    # Aggiungi la sigla al nome del file
    for file in filtered_files:
        # Dividi il nome del file e l'estensione
        name, ext = os.path.splitext(file)
        # Crea il nuovo nome del file
        new_name = f"{name}_{sigla}{ext}"
        # Rinomina il file
        os.rename(os.path.join(target_directory, file), os.path.join(target_directory, new_name))
        print(f"Rinominato: {file} -> {new_name}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: add_sigla.py <directory> <filtro> <sigla>")
        sys.exit(1)
    directory = sys.argv[1]
    filter_string = sys.argv[2]
    sigla = sys.argv[3]
    add_sigla(directory, filter_string, sigla)
