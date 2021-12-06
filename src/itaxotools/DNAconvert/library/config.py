#!/usr/bin/env python3

from typing import Optional
from dataclasses import dataclass
from pathlib import Path
import json

import appdirs


@dataclass
class Config():
    nexus_parser: str = "internal"


def _read_config() -> Optional[Config]:
    """
    Reads `DNAconvert/config.json` in `user_config_dir`
    """
    config_path = Path(appdirs.user_config_dir(
        appname="DNAconvert", appauthor="iTaxoTools")) / "config.json"
    if not config_path.exists():
        return None
    try:
        with open(config_path) as config_file:
            config_dict = json.load(config_file)
        return Config(**config_dict)
    except json.JSONDecodeError:
        print("config.json is not a JSON")
        return None
    except TypeError:
        print("Cannot parse config.json")
        return None


def get_config() -> Config:
    return _read_config() or Config()
