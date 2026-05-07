import re
import logging
from typing import Any
from pathlib import Path
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, File, UploadFile

logger = logging.getLogger(__name__)
router = APIRouter(prefix='/api/{thread_id}', tags=["uploads"])

UTF8 = 'utf-8'
NAME_PATTERN = re.compile(r"^[A-Za-z0-9-]+$")
root = Path(__file__).parent.parent.parent.parent.parent / "images"


class UploadResponse(BaseModel):
    code: int = Field(default=200, description="status code")
    success: bool
    img_list: list[dict[str, Any]] = Field(default_factory=list)


# 获取上传文件夹路径
def get_upload_dir(thread_id: str) -> Path:
    upload_path = root / thread_id
    if not upload_path.exists():
        upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


# 查看文件是否存在
def check_file_exist(thread_id: str, file_name: str) -> Path | None:
    path = root / thread_id
    if not path.exists():
        logger.info(f"{path} not found")
        return None
    file = path / file_name
    if not file.exists():
        logger.info(f"{file} not found")
        return None
    return file


@router.post(
    "/upload",
    response_model=UploadResponse
)
async def upload_files(
        thread_id: str,
        files: list[UploadFile] = File(...)
) -> UploadResponse:
    """
    upload multiple file support image,pdf...
    args:
        files: file
    response:
    {
      "code": 200,
      "success": true,
      "img_list": [
        {
          "file_name": "1764826928.png",
          "size": 1631829,
          "content-type": "image/png"
        }
      ]
    }
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files found")

    upload_path = get_upload_dir(thread_id)

    file_list: list[dict[str, Any]] = []
    try:
        for file in files:
            safe_filename = Path(file.filename).name
            if not safe_filename or safe_filename in {".", ".."} or "/" in safe_filename or "\\" in safe_filename:
                logger.warning(f"Skipping file with unsafe filename: {file.filename!r}")
                continue

            img = await file.read()
            upload_file = upload_path / file.filename
            upload_file.write_bytes(img)

            file_info = {
                "file_name": file.filename,
                "size": file.size,
                "content-type": file.content_type,
            }

            file_list.append(file_info)
    except Exception as e:
        raise e
    return UploadResponse(
        code=200,
        success=True,
        img_list=file_list,
    )


@router.delete(
    "/{file_name}"
)
async def remove_file(
        thread_id: str,
        file_name: str
) -> dict[str, Any]:
    """
    delete single file
    args:
        file_name: file name
    response:    {
      "code": 200,
      "msg": "1764826928.png delete success"
    }
    """
    if not thread_id:
        raise HTTPException(status_code=422, detail="thread_id not empty")
    if not file_name:
        raise HTTPException(status_code=422, detail="file name not empty")

    file_exist = check_file_exist(thread_id, file_name)
    if file_exist:
        file_exist.unlink()
        return {
            "code": 200,
            "msg": f'{file_exist.name} delete success'
        }
    return {
        "code": 422,
        "msg": "file not found"
    }
