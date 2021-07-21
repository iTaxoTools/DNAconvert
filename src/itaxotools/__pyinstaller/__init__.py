#!/usr/bin/env python3

from typing import List
import os


def get_hook_dirs() -> List[str]:
    return [os.path.dirname(__file__)]


def get_pyinstaller_tests() -> List[str]:
    return [os.path.dirname(__file__)]
