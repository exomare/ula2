#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys

__date__ = "21-11-2024"
__version__ = "0.1.0"
__author__ = "Marta Materni"

def convert_to_windows_format(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    content = content.replace('\n', '\r\n')
    return content

def main(source_dir):
    if not os.path.isdir(source_dir):
        print(f"La directory {source_dir} non esiste.")
        return
    new_dir = source_dir + '_wnd'
    os.makedirs(new_dir, exist_ok=True)
    for file_name in os.listdir(source_dir):
        file_path = os.path.join(source_dir, file_name)
        if os.path.isfile(file_path):
            content = convert_to_windows_format(file_path)
            new_file_path = os.path.join(new_dir, file_name)
            with open(new_file_path, 'w') as new_file:
                new_file.write(content)
            os.chmod(new_file_path, 0o777)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python ualx2w.py <directory_sorgente>")
    else:
        source_dir = sys.argv[1]
        main(source_dir)
