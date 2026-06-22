import re
import logging
from pathlib import Path
from zipfile import ZipFile
from pydantic import Field, BaseModel
from tempfile import TemporaryDirectory
from backend.tina.config.paths import SKILL_PATH
from backend.tina.skills import Skill, load_skills, _validate_skill_frontmatter
from fastapi import APIRouter, HTTPException, UploadFile, File

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/skill", tags=["skill"])


# skill base class
class SkillResponse(BaseModel):
    code: int = Field(default=200, description="status code")
    msg: str
    skill_name: str = Field(description="skill name")


def check_skill_dir() -> Path:
    if not SKILL_PATH.exists():
        SKILL_PATH.mkdir(parents=True, exist_ok=True)
    return SKILL_PATH


@router.post(
    "/install",
    response_model=SkillResponse,
)
async def install_skill(file: UploadFile = File(...)):
    """
    install skill zip
    args:
        file
    response:
    {
      "code": 200,
      "msg": "backend_design install success",
      "skill_name": "backend_design"
    }
    """
    if not file:
        raise HTTPException(status_code=401, detail="未发现文件")

    if not file.filename.endswith((".zip", ".tar")):
        raise HTTPException(status_code=401, detail="文件后缀错误")
    # 获取存放skill文件夹
    skill_path = check_skill_dir()
    # 创建临时文件夹
    with TemporaryDirectory() as tmpdir:
        temp_path = Path(tmpdir) / file.filename
        content = await file.read()
        temp_path.write_bytes(content)
        with ZipFile(temp_path, "r") as zf:
            total_size = sum(info.file_size for info in zf.infolist())
            if total_size > 100 * 1024 * 1024:
                raise ValueError("Skill archive too large when extracted (>100MB)")
            for info in zf.infolist():
                if (
                    Path(info.filename).is_absolute()
                    or ".." in Path(info.filename).parts
                ):
                    raise ValueError(f"Unsafe path in archive: {info.filename}")
            # 提取压缩包中的所有内容
            zf.extractall(skill_path)
            # 验证skill文件是否有效
            file_name = file.filename.split(".")[0]
            skill_dir = skill_path / file_name
            is_valid, message, skill_name = _validate_skill_frontmatter(skill_dir)
            if not is_valid:
                raise ValueError(f"invalid skill: {message}")
            if not re.fullmatch(r"[a-zA-Z0-9_-]+", skill_name):
                raise ValueError("invalid skill name", skill_name)

    return SkillResponse(
        code=200,
        msg=f"{file_name} install success",
        skill_name=f"{file_name}",
    )


@router.delete(
    "/uninstall/{skill_name}",
    response_model=SkillResponse,
)
async def remove_skill(skill_name: str) -> SkillResponse:
    """
    delete skill
    args:
        skill name
    response:
    {
      "code": 200,
      "msg": "backend_design delete success",
      "skill_name": "backend_design"
    }
    """
    if not skill_name:
        raise HTTPException(status_code=401, detail="skill name not empty")

    skill_path = SKILL_PATH / skill_name
    if not skill_path.exists():
        raise HTTPException(status_code=401, detail="not found skill")
    # clear all file
    for file in skill_path.iterdir():
        if file.is_file():
            file.unlink()
    # clear directory
    skill_path.rmdir()
    logger.info(f"delete skill {skill_name}")

    return SkillResponse(
        code=200,
        msg=f"{skill_name} delete success",
        skill_name=skill_name,
    )


@router.get("/list")
async def list_skill() -> list[Skill]:
    """list all skill"""
    skill_list = load_skills(SKILL_PATH)
    return skill_list
