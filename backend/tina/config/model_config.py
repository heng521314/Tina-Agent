import json
from typing import Any
from backend.tina.config.paths import MODEL_PATH


# Verify if the configuration file exists.
def _validata_config():
    if not MODEL_PATH.exists():
        MODEL_PATH.touch()
        return False
    return True


# Analyze configuration file
def parse_model_config() -> str | dict:
    is_validate = _validata_config()
    if is_validate:
        with open(MODEL_PATH, "r") as f:
            data: dict[str, dict[str, Any]] = json.load(f)
        return data
    else:
        return f"配置文件创建在{MODEL_PATH},配置后使用"
