import json
from pathlib import Path
from typing import Any

model_path = Path(__file__).parent.parent.parent.parent / "model_config.json"


# 验证配置文件是否存在
def _validata_config():
    if not model_path.exists():
        model_path.touch()
        return False
    return True


# 解析配置文件
def parse_model_config() -> str | dict:
    is_validate = _validata_config()
    if is_validate:
        with open(model_path, 'r') as f:
            data: dict[str, dict[str, Any]] = json.load(f)
        return data
    else:
        return f'配置文件创建在{model_path},配置后使用'
