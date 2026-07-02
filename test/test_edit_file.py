from backend.tina.tools.base_tools import edit_file
from pathlib import Path


def test(p: Path, old: str, new: str):
    assert edit_file(p, old, new) == "edit file complete"


if __name__ == '__main__':
    p = Path(__file__).parent.parent / "main.py"
    test(p, "test1", "test12")
