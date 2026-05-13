from pathlib import Path
from backend.tina.skills.parser import parse_skill_file
from backend.tina.config.paths import SKILL_PATH


def load_skills(skills_path: Path | None = None, enabled_only: bool = False) -> list:
    """
    Load all skills from the skills directory.

    Scans all skill directories, parsing SKILL.md files
    to extract metadata. The enabled state is determined by the skills_state_config.json file.

    Args:
        skills_path: Optional custom path to skills directory.
        enabled_only: If True, only return enabled skills (default: False)

    Returns:
        List of Skill objects, sorted by name
    """
    if skills_path is None:
        skills_path = SKILL_PATH

    if not skills_path.exists():
        return []

    skills = []

    for path in skills_path.iterdir():
        if path.is_file():
            continue
        skill_file = path / "SKILL.md"
        skill = parse_skill_file(skill_file)
        if skill:
            skills.append(skill)

    if enabled_only:
        skills = [skill for skill in skills if skill.enabled]

    # Sort by name for consistent ordering
    skills.sort(key=lambda s: s.name)

    return skills
