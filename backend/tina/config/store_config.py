import yaml
from pathlib import Path
from typing import Dict, Any
from backend.tina.config.paths import DB_PATH

"""Check if the database configuration file exists."""


def check_config_exist(p: Path) -> bool:
    if not p.exists():
        p.touch()
        return False
    return True


"""Analyze database configuration file"""


def parse_db_config() -> str | dict:
    is_exist = check_config_exist(DB_PATH)
    if is_exist:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            config: Dict[str, Dict[str, Any]] = yaml.safe_load(f)
            return config
    else:
        return f"The configuration file has been created at: {DB_PATH}. Please use it after configuration."
