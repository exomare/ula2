#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__date__ = "21-11-2024"
__version__ = "0.1.0"
__author__ = "Marta Materni"

import stat
from pathlib import Path


def set_permissions(path):
    path.chmod(stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)

def ulachmod(directory):
    for item in directory.rglob('*'):
        set_permissions(item)
        print(f"{item}")

if __name__ == "__main__":
    current_directory = Path.cwd()
    ulachmod(current_directory)
